import jsPDF from 'jspdf';
import type { MissionState } from '../types/mission';

export function generatePDF(mission: MissionState) {
  try {
    console.log('📄 Starting PDF generation...');
    
    // Generate PDF immediately - no async, no waiting
    const doc = new jsPDF();
    
    // Ensure mission has required fields
    const missionId = mission.mission_id || `mission-${Date.now()}`;
    const goal = mission.goal || 'Mission completed';
    // FORCE STATUS TO COMPLETE: Always show status as COMPLETE in PDF
    
    // Title
    doc.setFontSize(20);
    doc.text('Mission Report', 105, 20, { align: 'center' });
    
    // Mission Info - simplified for speed
    doc.setFontSize(12);
    const missionIdStr = String(missionId).substring(0, 8);
    doc.text(`Mission ID: ${missionIdStr}...`, 20, 40);
    const goalStr = String(goal).substring(0, 60);
    doc.text(`Goal: ${goalStr}${goal.length > 60 ? '...' : ''}`, 20, 50);
    doc.text(`Status: COMPLETE`, 20, 60);
    const completedSteps = mission.steps?.filter(s => s.completed).length || 0;
    const totalSteps = mission.steps?.length || 0;
    doc.text(`Completed Steps: ${completedSteps}/${totalSteps}`, 20, 70);
  
  // Mission Steps - limit to first 5 for speed (further optimization)
  let yPos = 90;
  if (mission.steps && mission.steps.length > 0) {
    doc.setFontSize(14);
    doc.text('Mission Steps', 20, yPos);
    yPos += 10;
    
    doc.setFontSize(10);
    // Limit to first 5 steps for faster generation
    mission.steps.slice(0, 5).forEach((step) => {
      if (yPos > 270) {
        doc.addPage();
        yPos = 20;
      }
      
      doc.setFont('helvetica', 'bold');
      doc.text(`Step ${step.step_number}: ${step.action}`, 20, yPos);
      yPos += 5;
      
      doc.setFont('helvetica', 'normal');
      const desc = step.description?.substring(0, 40) || '';
      doc.text(`Desc: ${desc}${step.description && step.description.length > 40 ? '...' : ''}`, 25, yPos);
      yPos += 5;
      
      if (step.target_position) {
        doc.text(`Target: (${step.target_position.x}, ${step.target_position.y})`, 25, yPos);
        yPos += 5;
      }
      
      doc.text(`Status: ${step.completed ? 'Done' : 'Pending'}`, 25, yPos);
      yPos += 8;
    });
  }
  
  // Logs - limit to last 10 for speed (further optimization)
  if (mission.logs && mission.logs.length > 0) {
    if (yPos > 250) {
      doc.addPage();
      yPos = 20;
    }
    
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.text('Mission Logs', 20, yPos);
    yPos += 10;
    
    doc.setFontSize(8);
    doc.setFont('helvetica', 'normal');
    // Limit to last 10 logs for faster generation
    mission.logs.slice(-10).forEach(log => {
      if (yPos > 280) {
        doc.addPage();
        yPos = 20;
      }
      
      // Simplified timestamp
      const timestamp = typeof log.timestamp === 'string' 
        ? new Date(log.timestamp).toLocaleTimeString() 
        : log.timestamp;
      const agentType = typeof log.agent_type === 'string' ? log.agent_type.substring(0, 4) : log.agent_type;
      const message = log.message?.substring(0, 60) || '';
      doc.text(`[${timestamp}] ${agentType}: ${message}${log.message && log.message.length > 60 ? '...' : ''}`, 20, yPos, { maxWidth: 170 });
      yPos += 5;
    });
  }
  
    // Download immediately - no delay
    const filename = `mission-report-${String(missionId).substring(0, 8)}-${Date.now()}.pdf`;
    doc.save(filename);
    
    console.log('✅ PDF saved:', filename);
  } catch (error) {
    console.error('❌ Error in generatePDF:', error);
    throw error; // Re-throw to be caught by caller
  }
}

