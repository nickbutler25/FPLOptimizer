import { 
  ApiStatus, 
  ValidationErrorCode,
  DataSource,
  CacheStatus,
  LogLevel
} from '../types/fpl.types';

export interface ApiResponse<T = unknown> {
  readonly status: ApiStatus;
  readonly data?: T;
  readonly message?: string;
  readonly timestamp?: string;
  readonly request_id?: string;
  readonly errors?: readonly ValidationError[];
  readonly metadata?: ResponseMetadata;
}

export interface ResponseMetadata {
  readonly data_source?: DataSource;
  readonly cache_status?: CacheStatus;
  readonly execution_time?: number; // milliseconds
  readonly api_version?: string;
  readonly rate_limit_remaining?: number;
  readonly rate_limit_reset?: string;
}

export interface ValidationError {
  readonly field: string;
  readonly message: string;
  readonly code: ValidationErrorCode;
  readonly value?: unknown;
  readonly severity?: 'error' | 'warning' | 'info';
}
