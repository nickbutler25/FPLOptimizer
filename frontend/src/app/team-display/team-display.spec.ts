import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TeamDisplay } from './team-display';

describe('TeamDisplay', () => {
  let component: TeamDisplay;
  let fixture: ComponentFixture<TeamDisplay>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TeamDisplay]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TeamDisplay);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
