import { TestBed } from '@angular/core/testing';

import { FplOptimizer } from './fpl-optimizer';

describe('FplOptimizer', () => {
  let service: FplOptimizer;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(FplOptimizer);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
