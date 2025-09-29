package com.geoattend.user.controller;

import com.geoattend.user.dto.AuthRequest;
import com.geoattend.user.dto.AuthResponse;
import com.geoattend.user.dto.UserRequest;
import com.geoattend.user.service.UserService;
import jakarta.validation.Valid;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/auth")
public class AuthController {

    private static final Logger log = LoggerFactory.getLogger(AuthController.class);
    private final UserService userService;

    public AuthController(UserService userService) {
        this.userService = userService;
    }

    @PostMapping("/register")
    public ResponseEntity<AuthResponse> register(@Valid @RequestBody UserRequest request) {
        log.info("POST /auth/register - Registrando usuario: {}", request.getEmail());

        AuthResponse response = userService.register(request);

        log.info("Usuario registrado exitosamente: {}", request.getEmail());
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    @PostMapping("/login")
    public ResponseEntity<AuthResponse> login(@Valid @RequestBody AuthRequest request) {
        log.info("POST /auth/login - Intentando autenticar: {}", request.getEmail());

        AuthResponse response = userService.authenticate(request);

        log.info("Autenticación exitosa para: {}", request.getEmail());
        return ResponseEntity.ok(response);
    }

    @PostMapping("/logout")
    public ResponseEntity<Void> logout(@RequestHeader("Authorization") String authHeader) {
        log.info("POST /auth/logout - Cerrando sesión");

        // TODO: Implementar blacklist de tokens o invalidación en Redis
        // Por ahora, el logout es manejado del lado del cliente eliminando el token

        log.info("Sesión cerrada exitosamente");
        return ResponseEntity.ok().build();
    }

    @GetMapping("/health")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("Auth service is running");
    }
}