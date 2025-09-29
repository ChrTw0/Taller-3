package com.geoattend.user.service;

import com.geoattend.user.dto.AuthRequest;
import com.geoattend.user.dto.AuthResponse;
import com.geoattend.user.dto.UserRequest;
import com.geoattend.user.dto.UserResponse;
import com.geoattend.user.entity.User;
import com.geoattend.user.entity.UserProfile;
import com.geoattend.user.exception.UserAlreadyExistsException;
import com.geoattend.user.exception.UserNotFoundException;
import com.geoattend.user.repository.UserRepository;
import com.geoattend.user.security.JwtService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Service
@Transactional
public class UserService implements UserDetailsService {

    private static final Logger log = LoggerFactory.getLogger(UserService.class);

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;
    private final AuthenticationManager authenticationManager;

    public UserService(UserRepository userRepository, PasswordEncoder passwordEncoder,
                      JwtService jwtService, AuthenticationManager authenticationManager) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtService = jwtService;
        this.authenticationManager = authenticationManager;
    }

    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        return userRepository.findByEmail(username)
                .orElseThrow(() -> new UsernameNotFoundException("Usuario no encontrado: " + username));
    }

    public AuthResponse register(UserRequest request) {
        log.info("Registrando nuevo usuario con email: {}", request.getEmail());

        // Validar que el usuario no exista
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new UserAlreadyExistsException("Ya existe un usuario con el email: " + request.getEmail());
        }

        if (userRepository.existsByCode(request.getCode())) {
            throw new UserAlreadyExistsException("Ya existe un usuario con el código: " + request.getCode());
        }

        // Crear usuario
        User user = User.builder()
                .code(request.getCode())
                .name(request.getName())
                .email(request.getEmail())
                .password(passwordEncoder.encode(request.getPassword()))
                .role(request.getRole() != null ? request.getRole() : User.Role.STUDENT)
                .status(User.UserStatus.ACTIVE)
                .build();

        // Crear perfil si se proporcionan datos
        if (request.getPhone() != null || request.getAcademicProgram() != null || request.getSemester() != null) {
            UserProfile profile = UserProfile.builder()
                    .user(user)
                    .phone(request.getPhone())
                    .academicProgram(request.getAcademicProgram())
                    .semester(request.getSemester())
                    .build();
            user.setProfile(profile);
        }

        user = userRepository.save(user);
        log.info("Usuario registrado exitosamente con ID: {}", user.getId());

        // Generar tokens
        String accessToken = jwtService.generateToken(user);
        String refreshToken = jwtService.generateRefreshToken(user);

        return AuthResponse.of(
                accessToken,
                refreshToken,
                jwtService.getExpirationTime() / 1000,
                UserResponse.from(user)
        );
    }

    public AuthResponse authenticate(AuthRequest request) {
        log.info("Intentando autenticar usuario: {}", request.getEmail());

        // Autenticar
        Authentication authentication = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(request.getEmail(), request.getPassword())
        );

        User user = (User) authentication.getPrincipal();

        // Actualizar último login
        userRepository.updateLastLogin(user.getId(), LocalDateTime.now());

        // Generar tokens
        String accessToken = jwtService.generateToken(user);
        String refreshToken = jwtService.generateRefreshToken(user);

        log.info("Usuario autenticado exitosamente: {}", user.getEmail());

        return AuthResponse.of(
                accessToken,
                refreshToken,
                jwtService.getExpirationTime() / 1000,
                UserResponse.from(user)
        );
    }

    @Transactional(readOnly = true)
    public UserResponse getUserById(Long id) {
        User user = userRepository.findById(id)
                .orElseThrow(() -> new UserNotFoundException("Usuario no encontrado con ID: " + id));
        return UserResponse.from(user);
    }

    @Transactional(readOnly = true)
    public UserResponse getUserByEmail(String email) {
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new UserNotFoundException("Usuario no encontrado con email: " + email));
        return UserResponse.from(user);
    }

    @Transactional(readOnly = true)
    public UserResponse getUserByCode(String code) {
        User user = userRepository.findByCode(code)
                .orElseThrow(() -> new UserNotFoundException("Usuario no encontrado con código: " + code));
        return UserResponse.from(user);
    }

    @Transactional(readOnly = true)
    public List<UserResponse> getAllUsers() {
        return userRepository.findAll()
                .stream()
                .map(UserResponse::from)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public Page<UserResponse> getAllUsers(Pageable pageable) {
        return userRepository.findAll(pageable)
                .map(UserResponse::from);
    }

    @Transactional(readOnly = true)
    public List<UserResponse> getUsersByRole(User.Role role) {
        return userRepository.findByRole(role)
                .stream()
                .map(UserResponse::from)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<UserResponse> getUsersByStatus(User.UserStatus status) {
        return userRepository.findByStatus(status)
                .stream()
                .map(UserResponse::from)
                .collect(Collectors.toList());
    }

    public UserResponse updateUser(Long id, UserRequest request) {
        log.info("Actualizando usuario con ID: {}", id);

        User user = userRepository.findById(id)
                .orElseThrow(() -> new UserNotFoundException("Usuario no encontrado con ID: " + id));

        // Actualizar campos del usuario
        if (request.getName() != null) {
            user.setName(request.getName());
        }

        if (request.getPassword() != null) {
            user.setPassword(passwordEncoder.encode(request.getPassword()));
        }

        if (request.getRole() != null) {
            user.setRole(request.getRole());
        }

        // Actualizar perfil
        UserProfile profile = user.getProfile();
        if (profile == null) {
            profile = new UserProfile();
            profile.setUser(user);
            user.setProfile(profile);
        }

        if (request.getPhone() != null) {
            profile.setPhone(request.getPhone());
        }

        if (request.getAcademicProgram() != null) {
            profile.setAcademicProgram(request.getAcademicProgram());
        }

        if (request.getSemester() != null) {
            profile.setSemester(request.getSemester());
        }

        user = userRepository.save(user);
        log.info("Usuario actualizado exitosamente: {}", user.getEmail());

        return UserResponse.from(user);
    }

    public void deactivateUser(Long id) {
        log.info("Desactivando usuario con ID: {}", id);

        User user = userRepository.findById(id)
                .orElseThrow(() -> new UserNotFoundException("Usuario no encontrado con ID: " + id));

        user.setStatus(User.UserStatus.INACTIVE);
        userRepository.save(user);

        log.info("Usuario desactivado exitosamente: {}", user.getEmail());
    }

    public void deleteUser(Long id) {
        log.info("Eliminando usuario con ID: {}", id);

        if (!userRepository.existsById(id)) {
            throw new UserNotFoundException("Usuario no encontrado con ID: " + id);
        }

        userRepository.deleteById(id);
        log.info("Usuario eliminado exitosamente con ID: {}", id);
    }

    @Transactional(readOnly = true)
    public boolean existsByEmail(String email) {
        return userRepository.existsByEmail(email);
    }

    @Transactional(readOnly = true)
    public boolean existsByCode(String code) {
        return userRepository.existsByCode(code);
    }
}