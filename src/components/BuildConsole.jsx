import React, { useState, useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import '../styles/build-console.css';

/**
 * BuildConsole Component
 * Bottom-left panel for controlling and monitoring the build process.
 * Displays start/stop buttons, build status, and real-time logs.
 */
function BuildConsole({
  onBuildStart,
  onBuildStop,
  buildStatus = 'idle',
  logs = [],
  currentTask = null,
  completedTasks = 0,
  totalTasks = 0,
  generatedFiles = 0,
}) {
  const [isExpanded, setIsExpanded] = useState(true);
  const logsEndRef = useRef(null);

  // Auto-scroll to bottom of logs
  useEffect(() => {
    if (logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  // Status badge configuration
  const statusConfig = {
    idle: { label: 'Idle', className: 'status-idle' },
    running: { label: 'Running', className: 'status-running' },
    done: { label: 'Complete', className: 'status-done' },
    error: { label: 'Error', className: 'status-error' },
    paused: { label: 'Paused', className: 'status-paused' },
  };

  const currentStatus = statusConfig[buildStatus] || statusConfig.idle;
  const progress = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  const handleStartClick = () => {
    if (onBuildStart) {
      onBuildStart();
    }
  };

  const handleStopClick = () => {
    if (onBuildStop) {
      onBuildStop();
    }
  };

  const handleToggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  const formatLogTimestamp = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  };

  const getLogClassName = (logEntry) => {
    if (logEntry.level === 'error') return 'log-error';
    if (logEntry.level === 'warn') return 'log-warn';
    if (logEntry.level === 'success') return 'log-success';
    if (logEntry.level === 'info') return 'log-info';
    return 'log-default';
  };

  return (
    <div className={`build-console ${isExpanded ? 'expanded' : 'collapsed'}`} data-testid="build-console">
      {/* Console Header */}
      <div className="build-console-header" onClick={handleToggleExpand}>
        <div className="build-console-title">
          <span className="console-icon">⚙️</span>
          <span>Build Console</span>
        </div>
        <div className="build-console-controls">
          {/* Status Indicator */}
          <span className={`status-badge ${currentStatus.className}`} data-testid="build-status">
            {currentStatus.label}
          </span>

          {/* Start/Stop Buttons */}
          {buildStatus === 'idle' || buildStatus === 'done' || buildStatus === 'error' ? (
            <button
              className="btn btn-start"
              onClick={(e) => {
                e.stopPropagation();
                handleStartClick();
              }}
              disabled={buildStatus === 'running'}
              data-testid="start-build-button"
            >
              ▶ Start Build
            </button>
          ) : (
            <button
              className="btn btn-stop"
              onClick={(e) => {
                e.stopPropagation();
                handleStopClick();
              }}
              data-testid="stop-build-button"
            >
              ⏹ Stop
            </button>
          )}

          {/* Expand/Collapse Toggle */}
          <span className="toggle-icon">{isExpanded ? '▼' : '▲'}</span>
        </div>
      </div>

      {/* Console Body */}
      {isExpanded && (
        <div className="build-console-body">
          {/* Progress Section */}
          <div className="build-progress" data-testid="build-progress">
            <div className="progress-info">
              <span className="progress-text">
                Task {completedTasks} of {totalTasks}
              </span>
              <span className="progress-percent">{progress}%</span>
            </div>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${progress}%` }}
                data-testid="progress-bar-fill"
              />
            </div>
            <div className="progress-stats">
              <span className="stat" data-testid="file-count">
                📁 {generatedFiles} files generated
              </span>
              <span className="stat" data-testid="task-progress">
                📋 {currentTask ? `Current: ${currentTask}` : 'Waiting...'}
              </span>
            </div>
          </div>

          {/* Logs Section */}
          <div className="build-logs" data-testid="build-logs">
            <div className="logs-header">
              <span>📜 Build Logs</span>
              <span className="logs-count">{logs.length} entries</span>
            </div>
            <div className="logs-content">
              {logs.length === 0 ? (
                <div className="logs-empty">No logs yet. Start a build to see output.</div>
              ) : (
                logs.map((log, index) => (
                  <div
                    key={log.id || index}
                    className={`log-entry ${getLogClassName(log)}`}
                    data-testid={`log-entry-${index}`}
                  >
                    <span className="log-timestamp">{formatLogTimestamp(log.timestamp)}</span>
                    <span className="log-message">{log.message}</span>
                  </div>
                ))
              )}
              <div ref={logsEndRef} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

BuildConsole.propTypes = {
  /** Callback when build starts */
  onBuildStart: PropTypes.func,
  /** Callback when build stops */
  onBuildStop: PropTypes.func,
  /** Current build status: idle, running, done, error, paused */
  buildStatus: PropTypes.oneOf(['idle', 'running', 'done', 'error', 'paused']),
  /** Array of log entries */
  logs: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
      message: PropTypes.string.isRequired,
      level: PropTypes.oneOf(['info', 'warn', 'error', 'success']),
      timestamp: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    })
  ),
  /** Current task being processed */
  currentTask: PropTypes.string,
  /** Number of completed tasks */
  completedTasks: PropTypes.number,
  /** Total number of tasks */
  totalTasks: PropTypes.number,
  /** Number of files generated */
  generatedFiles: PropTypes.number,
};

export default BuildConsole;
