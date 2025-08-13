import { HealthStatus, LogLevel } from '../types/fpl.types';

export interface HealthCheckResponse {
  readonly status: HealthStatus;
  readonly message?: string;
  readonly timestamp: string;
  readonly uptime?: number; // in seconds
  readonly version?: string;
  readonly environment?: 'development' | 'staging' | 'production';
  readonly dependencies?: readonly DependencyStatus[];
  readonly system_metrics?: SystemMetrics;
}

export interface DependencyStatus {
  readonly name: string;
  readonly status: HealthStatus;
  readonly response_time?: number; // in ms
  readonly last_check?: string;
  readonly version?: string;
  readonly endpoint?: string;
}

export interface SystemMetrics {
  readonly cpu_usage?: number; // 0-100
  readonly memory_usage?: number; // 0-100
  readonly disk_usage?: number; // 0-100
  readonly active_connections?: number;
  readonly cache_hit_ratio?: number; // 0-1
}