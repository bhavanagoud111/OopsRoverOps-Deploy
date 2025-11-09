import { useRef, useState, useEffect } from 'react';
import { Button } from '../Button';
import { Card } from '../Card';
import { Download, CheckCircle, XCircle, ArrowLeft } from 'lucide-react';
import type { LogEntry } from '../AgentLogs';
import type { RoverPhoto } from '../../lib/nasaApi';
import { ImageWithFallback } from '../figma/ImageWithFallback';
import { generatePDF } from '../../services/pdfGenerator';
import { getMissionReport } from '../../services/api';

interface Position {
  x: number;
  y: number;
}

interface ReportData {
  missionGoal: string;
  logs: LogEntry[];
  path: Position[];
  roverPhoto: RoverPhoto | null;
  duration: string;
  missionState?: any;
  reportData?: any;
  currentMissionId?: string;
}

interface ReportPageProps {
  onNavigate: (page: string) => void;
  reportData: ReportData | null;
}

export function ReportPage({ onNavigate, reportData }: ReportPageProps) {
  const reportRef = useRef<HTMLDivElement>(null);
  const [fetchedReportData, setFetchedReportData] = useState<any>(null);

  // Fetch report data in background if mission ID is provided
  useEffect(() => {
    if (reportData?.currentMissionId && !reportData.reportData) {
      getMissionReport(reportData.currentMissionId)
        .then(data => {
          setFetchedReportData(data);
          console.log('✅ Report data fetched in background');
        })
        .catch(error => {
          console.error('Failed to fetch mission report:', error);
        });
    }
  }, [reportData?.currentMissionId]);

  if (!reportData) {
    return (
      <main className="flex-1 flex items-center justify-center">
        <Card className="text-center max-w-md">
          <h2 className="mb-4">No Mission Data</h2>
          <p className="text-[var(--color-text-secondary)] mb-6">
            Complete a mission first to generate a report.
          </p>
          <Button onClick={() => onNavigate('dashboard')} variant="primary">
            Go to Dashboard
          </Button>
        </Card>
      </main>
    );
  }

  const { missionGoal, logs, path, roverPhoto, duration, missionState, reportData: reportDataFromBackend } = reportData;
  
  // Use fetched report data if available, otherwise use passed data
  const actualReportData = fetchedReportData || reportDataFromBackend;
  
  // Check mission status from missionState or reportData, fallback to logs
  const missionSuccess = 
    (missionState?.status === 'complete' || actualReportData?.status === 'complete') ||
    logs.some(log => 
      log.message.includes('Mission successful') || 
      log.message.includes('Target destination reached') ||
      log.message.includes('Mission completed successfully')
    );

  const handleDownload = () => {
    try {
      console.log('📄 Generating PDF report...');
      
      // CRITICAL FIX: Use actualReportData (correct mission) not missionState (might be current mission)
      // Always use the report data from backend which has the correct completed mission data
      let missionData: any = null;
      
      if (actualReportData && actualReportData.state) {
        // Use state from backend report - this is the correct completed mission
        missionData = actualReportData.state;
        console.log('✅ Using backend report state');
      } else if (actualReportData) {
        // Fallback: create from report data
        missionData = {
          mission_id: actualReportData.mission_id || `mission-${Date.now()}`,
          goal: actualReportData.goal || missionGoal || 'Mission completed',
          status: actualReportData.status || (missionSuccess ? 'complete' : 'incomplete'),
          current_step: actualReportData.steps_completed || path.length,
          rover_position: path.length > 0 ? path[path.length - 1] : { x: 0, y: 0 },
          obstacles: [],
          goal_positions: [],
          steps: actualReportData.steps || path.map((pos, idx) => ({
            step_number: idx + 1,
            action: 'move',
            target_position: pos,
            description: `Move to position (${pos.x}, ${pos.y})`,
            completed: true,
          })),
          logs: actualReportData.logs || logs.map(log => ({
            mission_id: actualReportData.mission_id || '',
            timestamp: new Date().toISOString(),
            agent_type: log.agent.toLowerCase(),
            message: log.message,
            level: log.type,
          })),
          agent_states: {},
          nasa_images: actualReportData.mission_photos || (roverPhoto ? [roverPhoto.img_src] : []),
          created_at: actualReportData.start_time || new Date().toISOString(),
          updated_at: actualReportData.end_time || new Date().toISOString(),
        };
        console.log('✅ Using report data fallback');
      } else if (missionState) {
        // Use missionState if available
        missionData = missionState;
        console.log('✅ Using missionState');
      } else {
        // Last resort: use current data
        missionData = {
          mission_id: `mission-${Date.now()}`,
          goal: missionGoal || 'Mission completed',
          status: missionSuccess ? 'complete' : 'incomplete',
          current_step: path.length,
          rover_position: path.length > 0 ? path[path.length - 1] : { x: 0, y: 0 },
          obstacles: [],
          goal_positions: [],
          steps: path.map((pos, idx) => ({
            step_number: idx + 1,
            action: 'move',
            target_position: pos,
            description: `Move to position (${pos.x}, ${pos.y})`,
            completed: true,
          })),
          logs: logs.map(log => ({
            mission_id: '',
            timestamp: new Date().toISOString(),
            agent_type: log.agent.toLowerCase(),
            message: log.message,
            level: log.type,
          })),
          agent_states: {},
          nasa_images: roverPhoto ? [roverPhoto.img_src] : [],
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };
        console.log('✅ Using minimal state');
      }
      
      // Ensure required fields exist
      if (!missionData.mission_id) {
        missionData.mission_id = `mission-${Date.now()}`;
      }
      if (!missionData.goal) {
        missionData.goal = missionGoal || 'Mission completed';
      }
      if (!missionData.steps) {
        missionData.steps = [];
      }
      if (!missionData.logs) {
        missionData.logs = [];
      }
      
      console.log('📥 Calling generatePDF with:', {
        mission_id: missionData.mission_id,
        goal: missionData.goal,
        steps: missionData.steps?.length || 0,
        logs: missionData.logs?.length || 0,
      });
      
      // Generate and download PDF
      generatePDF(missionData);
      
      console.log('✅ PDF generated successfully');
    } catch (error) {
      console.error('❌ Error generating PDF:', error);
      alert('Failed to generate PDF. Please check the console for details.');
    }
  };

  return (
    <main className="flex-1">
      <div className="max-w-[1440px] mx-auto px-6 py-8">
        <div className="mb-6">
          <Button
            onClick={() => onNavigate('dashboard')}
            variant="outline"
            size="sm"
            aria-label="Return to dashboard"
          >
            <ArrowLeft size={20} aria-hidden="true" />
            Back to Dashboard
          </Button>
        </div>

        <div ref={reportRef} className="space-y-6">
          {/* Header */}
          <header className="text-center mb-8">
            <h1 className="mb-4">Mission Report</h1>
            <div className="flex items-center justify-center gap-2">
              {missionSuccess ? (
                <>
                  <CheckCircle className="text-[var(--color-success)]" size={24} aria-hidden="true" />
                  <span className="text-[var(--color-success)]">Mission Successful</span>
                </>
              ) : (
                <>
                  <XCircle className="text-[var(--color-error)]" size={24} aria-hidden="true" />
                  <span className="text-[var(--color-error)]">Mission Incomplete</span>
                </>
              )}
            </div>
          </header>

          {/* Mission Summary */}
          <section aria-labelledby="summary-heading">
            <Card>
              <h2 id="summary-heading" className="mb-4">Mission Summary</h2>
              <dl className="space-y-3">
                <div>
                  <dt className="text-[var(--color-text-secondary)] mb-1">
                    <small>Mission Goal</small>
                  </dt>
                  <dd className="text-[var(--color-text-primary)]">{missionGoal}</dd>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <dt className="text-[var(--color-text-secondary)] mb-1">
                      <small>Waypoints</small>
                    </dt>
                    <dd className="text-[var(--color-text-primary)]">{path.length}</dd>
                  </div>
                  <div>
                    <dt className="text-[var(--color-text-secondary)] mb-1">
                      <small>Duration</small>
                    </dt>
                    <dd className="text-[var(--color-text-primary)]">{duration}</dd>
                  </div>
                  <div>
                    <dt className="text-[var(--color-text-secondary)] mb-1">
                      <small>Status</small>
                    </dt>
                    <dd className={missionSuccess ? 'text-[var(--color-success)]' : 'text-[var(--color-error)]'}>
                      {missionSuccess ? 'Success' : 'Incomplete'}
                    </dd>
                  </div>
                </div>
              </dl>
            </Card>
          </section>

          {/* NASA Imagery */}
          {roverPhoto && (
            <section aria-labelledby="imagery-heading">
              <Card>
                <h2 id="imagery-heading" className="mb-4">Captured NASA Rover Imagery</h2>
                <ImageWithFallback
                  src={roverPhoto.img_src}
                  alt={`Mars rover photo captured by ${roverPhoto.rover.name} on ${roverPhoto.earth_date}`}
                  className="w-full h-auto rounded-lg mb-3"
                />
                <p className="text-[var(--color-text-secondary)]">
                  <small>
                    Rover: {roverPhoto.rover.name} • Camera: {roverPhoto.camera.full_name} • Date: {roverPhoto.earth_date}
                  </small>
                </p>
              </Card>
            </section>
          )}

          {/* Activity Log */}
          <section aria-labelledby="log-heading">
            <Card>
              <h2 id="log-heading" className="mb-4">Mission Activity Log</h2>
              <div className="space-y-2 monospace max-h-96 overflow-y-auto">
                {logs.map((log) => (
                  <div
                    key={log.id}
                    className="p-3 bg-[var(--color-background)] rounded"
                  >
                    <p>
                      <small>
                        <span className="text-[var(--color-text-secondary)]">[{log.timestamp}]</span>
                        {' '}
                        <span className="text-[var(--color-primary)]">{log.agent}:</span>
                        {' '}
                        {log.message}
                      </small>
                    </p>
                  </div>
                ))}
              </div>
            </Card>
          </section>

              {/* Download Button */}
              <div className="flex justify-center">
                <Button
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    console.log('🔘 Download button clicked');
                    handleDownload();
                  }}
                  variant="primary"
                  size="lg"
                  aria-label="Download mission report"
                  type="button"
                >
                  <Download size={20} aria-hidden="true" />
                  Download Report
                </Button>
              </div>
        </div>
      </div>
    </main>
  );
}