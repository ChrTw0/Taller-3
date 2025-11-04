import { attendanceApi } from './api';
import type { OverallAttendanceStats } from '@/types/kpi';

export const kpiService = {
  getOverallAttendanceStats: async (startDate?: string, endDate?: string): Promise<OverallAttendanceStats> => {
    console.log('📊 KPI Service: Fetching overall attendance stats...');
    const stats = await attendanceApi.getOverallStats(startDate, endDate);
    return stats;
  },
};