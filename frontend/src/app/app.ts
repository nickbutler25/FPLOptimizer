// src/app/app.ts
import { CommonModule } from '@angular/common';
import { Component, OnDestroy, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { catchError, finalize, of, Subject, takeUntil, timeout } from 'rxjs';

// Services
import { ConfigService } from './config/config.service';
import { ServiceFactory } from './services/service-factory';

// Service Interfaces (for type safety)
import {
  HealthServiceInterface,
  OptimizerServiceInterface,
  PlayersServiceInterface,
  StatisticsServiceInterface
} from './services';

// Interfaces and Types
import {
  OptimizationRequest,
  OptimizationResult,
  Player,
  TeamStats
} from './object-interfaces';
import {
  BUDGET_CONSTRAINTS,
  Formation,
  FORMATION_CONFIG,
  FORMATIONS,
  FormRating,
  RiskTolerance
} from './types/fpl.types';

interface AdvancedOptions {
  excludeInjured: boolean;
  excludeDoubtful: boolean;
  riskTolerance: RiskTolerance;
  minFormRating?: number;
  prioritizeCaptaincy: boolean;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App implements OnInit, OnDestroy {
  // App Info
  readonly title = 'FPL Team Optimizer';
  readonly appVersion = '1.0.0';
  
  // Form Data
  budget: number = BUDGET_CONSTRAINTS.DEFAULT;
  formation: Formation = '3-5-2';
  
  // UI State
  isOptimizing = false;
  showAdvancedOptions = false;
  error: string | null = null;
  systemStatus: string | null = null;
  
  // NEW: Additional UI state for better UX
  optimizationTimeoutWarning = false;
  canCancelOptimization = false;
  
  // Results
  optimizationResult: OptimizationResult | null = null;
  teamStats: TeamStats | null = null;
  
  // Advanced Options
  advancedOptions: AdvancedOptions = {
    excludeInjured: true,
    excludeDoubtful: false,
    riskTolerance: 'balanced',
    minFormRating: 5,
    prioritizeCaptaincy: true
  };
  
  // Constants from config
  readonly formations = FORMATIONS;
  readonly budgetConstraints = BUDGET_CONSTRAINTS;
  
  // Services (created dynamically)
  private optimizerService!: OptimizerServiceInterface;
  private playersService!: PlayersServiceInterface;
  private healthService!: HealthServiceInterface;
  private statsService!: StatisticsServiceInterface;
  
  // Cleanup
  private destroy$ = new Subject<void>();
  
  // NEW: Optimization timeout and cancellation
  private optimizationTimeout = 30000; // 30 seconds
  private currentOptimization$ = new Subject<void>();

  constructor(
    public config: ConfigService,
    private serviceFactory: ServiceFactory
  ) {}

  ngOnInit(): void {
    this.initializeServices();
    this.initializeApp();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
    this.currentOptimization$.next();
    this.currentOptimization$.complete();
  }

  private initializeServices(): void {
    try {
      // Create services based on configuration
      this.optimizerService = this.serviceFactory.createOptimizerService();
      this.playersService = this.serviceFactory.createPlayersService();
      this.healthService = this.serviceFactory.createHealthService();
      this.statsService = this.serviceFactory.createStatisticsService();
      
      if (this.config.shouldLogToConsole) {
        console.log('🔧 Services initialized:');
        console.log('  - Optimizer:', this.optimizerService.constructor.name);
        console.log('  - Players:', this.playersService.constructor.name);
        console.log('  - Health:', this.healthService.constructor.name);
        console.log('  - Statistics:', this.statsService.constructor.name);
      }
    } catch (error) {
      console.error('❌ Failed to initialize services:', error);
      this.systemStatus = 'service_init_failed';
      this.error = 'Failed to initialize application services. Please refresh the page.';
      
      // Log detailed error for debugging
      this.logError('Service Initialization', error);
    }
  }

  private initializeApp(): void {
    if (this.config.shouldLogToConsole) {
      console.log('🚀 FPL Optimizer starting...');
      console.log('📡 API Base URL:', this.config.apiBaseUrl);
      console.log('🔧 Environment:', this.config.isProduction ? 'Production' : 'Development');
      console.log('🎮 Using Mock Data:', this.config.shouldUseMockData);
    }

    // Check system health
    this.checkSystemHealth();
    
    // Load initial data if needed
    this.loadInitialData();
  }

  private checkSystemHealth(): void {
    this.healthService.healthCheck()
      .pipe(
        takeUntil(this.destroy$),
        timeout(5000), // 5 second timeout for health check
        catchError(error => {
          console.error('❌ System health check failed:', error);
          return of({ status: 'unhealthy', error: error.message });
        })
      )
      .subscribe({
        next: (response) => {
          this.systemStatus = response.status;
          if (this.config.shouldLogToConsole) {
            console.log('✅ System health check passed:', response);
          }
        }
      });
  }

  private loadInitialData(): void {
    // Load sample players data to verify service connectivity
    this.playersService.getPlayers({ available_only: true })
      .pipe(
        takeUntil(this.destroy$),
        timeout(10000), // 10 second timeout
        catchError(error => {
          console.error('❌ Failed to load initial player data:', error);
          return of({ players: [], message: 'Failed to load player data' });
        })
      )
      .subscribe({
        next: (response) => {
          if (this.config.shouldLogToConsole && response.players) {
            console.log(`📋 Loaded ${response.players.length} available players`);
          }
        }
      });
  }

  // FIXED: Main optimization method with robust error handling
  optimizeTeam(): void {
    if (this.isOptimizing) return;
    
    // CRITICAL: Check if services are initialized
    if (!this.optimizerService) {
      this.handleOptimizationError('Optimization service not available. Please refresh the page and try again.');
      return;
    }
    
    this.startOptimization();
    
    if (this.config.shouldLogToConsole) {
      console.log(`🚀 Starting optimization: £${this.budget}m budget, ${this.formation} formation`);
    }

    try {
      this.optimizerService.optimize(this.budget, this.formation)
        .pipe(
          takeUntil(this.currentOptimization$),
          takeUntil(this.destroy$),
          timeout(this.optimizationTimeout),
          finalize(() => this.finishOptimization()), // CRITICAL: Always runs
          catchError(error => {
            // Handle errors and return a formatted error result
            console.error('❌ Optimization error caught:', error);
            return of({ 
              status: 'error', 
              message: this.formatErrorMessage(error),
              error: true 
            } as OptimizationResult);
          })
        )
        .subscribe({
          next: (result) => {
            if (result.status === 'error' || (result as any).error) {
              this.handleOptimizationError(result.message || 'Optimization failed');
            } else {
              this.handleOptimizationSuccess(result);
            }
          }
        });
    } catch (error) {
      // Catch synchronous errors (like service not initialized)
      this.finishOptimization();
      this.handleOptimizationError(this.formatErrorMessage(error));
      console.error('❌ Synchronous optimization error:', error);
    }
  }

  // FIXED: Advanced optimization with robust error handling
  optimizeAdvanced(): void {
    if (this.isOptimizing) return;
    
    // CRITICAL: Check if services are initialized
    if (!this.optimizerService) {
      this.handleOptimizationError('Optimization service not available. Please refresh the page and try again.');
      return;
    }
    
    this.startOptimization();
    
    if (this.config.shouldLogToConsole) {
      console.log('🚀 Starting advanced optimization with constraints:', this.advancedOptions);
    }
    
    const request: OptimizationRequest = {
      budget: this.budget,
      formation: this.formation,
      algorithm: 'linear_programming',
      constraints: {
        max_players_per_team: 3,
        exclude_injured: this.advancedOptions.excludeInjured,
        exclude_doubtful: this.advancedOptions.excludeDoubtful,
        min_form_rating: this.advancedOptions.minFormRating as FormRating
      },
      preferences: {
        risk_tolerance: this.advancedOptions.riskTolerance,
        prioritize_captaincy: this.advancedOptions.prioritizeCaptaincy,
        prefer_form: true
      }
    };
    
    try {
      this.optimizerService.optimizeAdvanced(request)
        .pipe(
          takeUntil(this.currentOptimization$),
          takeUntil(this.destroy$),
          timeout(this.optimizationTimeout),
          finalize(() => this.finishOptimization()), // CRITICAL: Always runs
          catchError(error => {
            console.error('❌ Advanced optimization error caught:', error);
            return of({ 
              status: 'error', 
              message: this.formatErrorMessage(error),
              error: true 
            } as OptimizationResult);
          })
        )
        .subscribe({
          next: (result) => {
            if (result.status === 'error' || (result as any).error) {
              this.handleOptimizationError(result.message || 'Advanced optimization failed');
            } else {
              this.handleOptimizationSuccess(result, true);
            }
          }
        });
    } catch (error) {
      // Catch synchronous errors
      this.finishOptimization();
      this.handleOptimizationError(this.formatErrorMessage(error));
      console.error('❌ Synchronous advanced optimization error:', error);
    }
  }

  // NEW: Retry functionality
  retryOptimization(): void {
    this.error = null;
    this.optimizeTeam();
  }

  // NEW: Cancel optimization
  cancelOptimization(): void {
    if (this.isOptimizing) {
      this.currentOptimization$.next(); // Cancel current request
      this.finishOptimization();
      this.error = 'Optimization cancelled by user.';
      
      if (this.config.shouldLogToConsole) {
        console.log('🛑 Optimization cancelled by user');
      }
    }
  }

  // IMPROVED: Start optimization with timeout warnings
  private startOptimization(): void {
    this.isOptimizing = true;
    this.error = null;
    this.optimizationResult = null;
    this.teamStats = null;
    this.optimizationTimeoutWarning = false;
    this.canCancelOptimization = false;

    // Reset cancellation subject
    this.currentOptimization$.next();
    
    // Show timeout warning after 15 seconds
    setTimeout(() => {
      if (this.isOptimizing) {
        this.optimizationTimeoutWarning = true;
        this.canCancelOptimization = true;
      }
    }, 15000);
  }

  // NEW: Finish optimization (always called via finalize)
  private finishOptimization(): void {
    this.isOptimizing = false;
    this.optimizationTimeoutWarning = false;
    this.canCancelOptimization = false;
    
    if (this.config.shouldLogToConsole) {
      console.log('🏁 Optimization finished');
    }
  }

  // IMPROVED: Format error messages for better user experience
  private formatErrorMessage(error: any): string {
    // Handle null/undefined service errors
    if (!this.optimizerService || !this.playersService || !this.healthService || !this.statsService) {
      return 'Application services not properly initialized. Please refresh the page and try again.';
    }
    
    if (error.name === 'TimeoutError') {
      return 'Optimization timed out. The server may be busy. Please try again.';
    }
    
    if (error.status) {
      switch (error.status) {
        case 400:
          return 'Invalid parameters. Please check your budget and formation settings.';
        case 401:
          return 'Authentication failed. Please refresh the page and try again.';
        case 403:
          return 'Access denied. Please check your permissions.';
        case 404:
          return 'Optimization service not found. Please contact support.';
        case 429:
          return 'Too many requests. Please wait a moment and try again.';
        case 500:
          return 'Server error. Please try again in a few moments.';
        case 502:
        case 503:
        case 504:
          return 'Service temporarily unavailable. Please try again later.';
        default:
          return `Server returned error ${error.status}. Please try again.`;
      }
    }
    
    if (error.message) {
      // Handle TypeError specifically (like the service undefined error)
      if (error.message.includes('Cannot read properties of undefined')) {
        return 'Application service error. Please refresh the page and try again.';
      }
      
      // Clean up common error messages
      if (error.message.includes('NetworkError') || error.message.includes('fetch')) {
        return 'Network connection failed. Please check your internet connection and try again.';
      }
      if (error.message.includes('JSON')) {
        return 'Invalid response from server. Please try again.';
      }
      return error.message;
    }
    
    return 'An unexpected error occurred. Please try again.';
  }

  // SAME: Success handler (no changes needed)
  private handleOptimizationSuccess(result: OptimizationResult, isAdvanced = false): void {
    if (this.config.shouldLogToConsole) {
      console.log(`✅ ${isAdvanced ? 'Advanced' : 'Basic'} optimization completed:`, result);
    }
    
    if (result.status === 'error') {
      this.handleOptimizationError(result.message || 'Optimization failed');
      return;
    }
    
    if (result.status === 'success' && result.players) {
      this.optimizationResult = result;
      
      // Generate team statistics
      this.teamStats = this.statsService.calculateTeamStats([...result.players]);
      
      // Scroll to results
      setTimeout(() => {
        const resultsElement = document.querySelector('[data-results]');
        if (resultsElement) {
          resultsElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }, 100);
      
      // Log optimization details
      if (this.config.shouldLogToConsole) {
        console.log(`⏱️ Optimization time: ${result.optimization_time}ms`);
        console.log(`🎯 Confidence score: ${(result.confidence_score || 0) * 100}%`);
        console.log(`🧮 Algorithm used: ${result.algorithm_used}`);
        console.log(`📊 Team stats:`, this.teamStats);
        
        if (result.warnings?.length) {
          result.warnings.forEach(warning => {
            console.warn(`⚠️ ${warning.severity.toUpperCase()}: ${warning.message}`);
          });
        }
      }
    }
  }

  // IMPROVED: Error handler with better UX
  private handleOptimizationError(errorMessage: string): void {
    this.error = errorMessage;
    
    // Scroll to error message
    setTimeout(() => {
      const errorElement = document.querySelector('[data-error]');
      if (errorElement) {
        errorElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }, 100);
    
    console.error('❌ Optimization error:', errorMessage);
  }

  // SAME: UI Helper Methods (no changes needed)
  clearResults(): void {
    this.optimizationResult = null;
    this.teamStats = null;
    this.error = null;
    
    if (this.config.shouldLogToConsole) {
      console.log('🗑️ Results cleared');
    }
  }

  getFormationDescription(formation: Formation): string {
    const config = FORMATION_CONFIG[formation];
    return config ? config.tactical_style : 'Unknown';
  }

  getFormationInfo(formation: Formation): string {
    const config = FORMATION_CONFIG[formation];
    if (!config) return '';
    
    return `${config.name} - ${config.description}`;
  }

  trackPlayer(index: number, player: Player): number {
    return player.id;
  }

  // Getters for template
  get showAdvancedOptimizeButton(): boolean {
    return this.config.isAdvancedOptimizationEnabled && this.showAdvancedOptions;
  }

  get hasOptimizationResult(): boolean {
    return this.optimizationResult?.status === 'success';
  }

  get hasWarnings(): boolean {
    return !!(this.optimizationResult?.warnings?.length);
  }

  get isFormValid(): boolean {
    return this.budget >= this.budgetConstraints.MIN && 
           this.budget <= this.budgetConstraints.MAX &&
           this.formations.includes(this.formation);
  }

  // NEW: Service status checker
  get servicesReady(): boolean {
    return !!(this.optimizerService && this.playersService && this.healthService && this.statsService);
  }

  get canOptimize(): boolean {
    return this.servicesReady && this.isFormValid && !this.isOptimizing;
  }

  // Development helpers (only shown in development mode)
  loadSampleTeam(): void {
    if (!this.config.isProduction) {
      console.log('🔧 Loading sample team (dev mode only)');
      this.budget = 100;
      this.formation = '3-5-2';
      this.optimizeTeam();
    }
  }

  logCurrentState(): void {
    if (!this.config.isProduction) {
      console.log('🔧 Current App State:', {
        budget: this.budget,
        formation: this.formation,
        advancedOptions: this.advancedOptions,
        hasResult: !!this.optimizationResult,
        isOptimizing: this.isOptimizing,
        systemStatus: this.systemStatus
      });
    }
  }

  // SAME: Error handling helper (no changes needed)
  private logError(context: string, error: any): void {
    const errorInfo = {
      context,
      message: error.message || 'Unknown error',
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href
    };
    
    console.error(`❌ ${context}:`, errorInfo);
    
    // In production, you might want to send this to an error tracking service
    if (this.config.isProduction) {
      // Example: this.errorTrackingService.logError(errorInfo);
    }
  }

  // Keyboard shortcuts (optional)
  onKeyboardShortcut(event: KeyboardEvent): void {
    if (event.ctrlKey || event.metaKey) {
      switch (event.key) {
        case 'Enter':
          if (!this.isOptimizing && this.isFormValid) {
            event.preventDefault();
            this.optimizeTeam();
          }
          break;
        case 'r':
          if (!this.config.isProduction) {
            event.preventDefault();
            this.clearResults();
          }
          break;
        case 'c':
          if (this.isOptimizing && this.canCancelOptimization) {
            event.preventDefault();
            this.cancelOptimization();
          }
          break;
      }
    }
  }
}