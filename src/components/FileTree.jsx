import React, { useState, useMemo } from 'react';
import PropTypes from 'prop-types';
import '../styles/file-tree.css';

/**
 * FileTree Component
 * Displays generated files in a tree structure.
 * Supports expand/collapse folders and file selection.
 */
function FileTree({
  files = [],
  onFileSelect,
  selectedFile = null,
  defaultExpanded = true,
  showFileCount = true,
  maxDepth = 10,
}) {
  const [expandedFolders, setExpandedFolders] = useState({});

  // Build tree structure from flat file list
  const fileTree = useMemo(() => {
    const tree = {};

    files.forEach((file) => {
      const parts = file.path.split(/[\\/]/);
      let current = tree;

      parts.forEach((part, index) => {
        const isFile = index === parts.length - 1;
        const fullPath = parts.slice(0, index + 1).join('/');

        if (isFile) {
          current[part] = {
            isFile: true,
            path: file.path,
            name: part,
            size: file.size,
            status: file.status || 'generated',
            extension: part.split('.').pop(),
          };
        } else {
          if (!current[part]) {
            current[part] = {
              isFile: false,
              path: fullPath,
              name: part,
              children: {},
            };
          }
          current = current[part].children;
        }
      });
    });

    return tree;
  }, [files]);

  // Initialize expanded state
  React.useEffect(() => {
    if (defaultExpanded) {
      const allFolders = {};
      const collectFolders = (node, path = '') => {
        Object.entries(node).forEach(([name, nodeData]) => {
          if (!nodeData.isFile) {
            const fullPath = path ? `${path}/${name}` : name;
            allFolders[fullPath] = true;
            collectFolders(nodeData.children, fullPath);
          }
        });
      };
      collectFolders(fileTree);
      setExpandedFolders(allFolders);
    }
  }, [fileTree, defaultExpanded]);

  const toggleFolder = (folderPath) => {
    setExpandedFolders((prev) => ({
      ...prev,
      [folderPath]: !prev[folderPath],
    }));
  };

  const handleFileClick = (file) => {
    if (file.isFile && onFileSelect) {
      onFileSelect(file);
    }
  };

  const getFileIcon = (extension) => {
    const icons = {
      js: '📜',
      jsx: '⚛️',
      ts: '📘',
      tsx: '⚛️',
      py: '🐍',
      rs: '🦀',
      json: '📋',
      md: '📝',
      css: '🎨',
      html: '🌐',
      toml: '⚙️',
      env: '🔐',
    };
    return icons[extension?.toLowerCase()] || '📄';
  };

  const getStatusClass = (status) => {
    const statusMap = {
      generated: 'status-generated',
      pending: 'status-pending',
      error: 'status-error',
      modified: 'status-modified',
    };
    return statusMap[status] || 'status-generated';
  };

  const renderTree = (node, depth = 0, path = '') => {
    if (depth >= maxDepth) return null;

    return Object.entries(node).map(([name, nodeData]) => {
      const currentPath = path ? `${path}/${name}` : name;
      const isExpanded = expandedFolders[currentPath];

      if (nodeData.isFile) {
        return (
          <div
            key={nodeData.path}
            className={`tree-item file-item ${selectedFile === nodeData.path ? 'selected' : ''} ${getStatusClass(nodeData.status)}`}
            style={{ paddingLeft: `${depth * 16 + 8}px` }}
            onClick={() => handleFileClick(nodeData)}
            data-testid={`file-tree-item-${name}`}
            data-file-path={nodeData.path}
          >
            <span className="file-icon">{getFileIcon(nodeData.extension)}</span>
            <span className="file-name">{name}</span>
            {nodeData.size && (
              <span className="file-size">{formatFileSize(nodeData.size)}</span>
            )}
          </div>
        );
      }

      return (
        <div key={currentPath} className="tree-folder" data-testid={`folder-${name}`}>
          <div
            className={`tree-item folder-item ${isExpanded ? 'expanded' : 'collapsed'}`}
            style={{ paddingLeft: `${depth * 16 + 8}px` }}
            onClick={() => toggleFolder(currentPath)}
            data-testid={`folder-toggle-${name}`}
          >
            <span className="folder-icon">{isExpanded ? '📂' : '📁'}</span>
            <span className="folder-name">{name}</span>
            {showFileCount && (
              <span className="folder-count">{countFiles(nodeData.children)}</span>
            )}
          </div>
          {isExpanded && (
            <div className="folder-children">
              {renderTree(nodeData.children, depth + 1, currentPath)}
            </div>
          )}
        </div>
      );
    });
  };

  const countFiles = (node) => {
    let count = 0;
    Object.values(node).forEach((nodeData) => {
      if (nodeData.isFile) {
        count++;
      } else {
        count += countFiles(nodeData.children);
      }
    });
    return count;
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const totalFiles = useMemo(() => countFiles(fileTree), [fileTree]);
  const totalFolders = useMemo(() => {
    let count = 0;
    const countFolders = (node) => {
      Object.values(node).forEach((nodeData) => {
        if (!nodeData.isFile) {
          count++;
          countFolders(nodeData.children);
        }
      });
    };
    countFolders(fileTree);
    return count;
  }, [fileTree]);

  return (
    <div className="file-tree-container" data-testid="file-tree">
      <div className="file-tree-header">
        <span className="header-title">📁 Generated Files</span>
        <span className="header-stats" data-testid="file-tree-stats">
          {totalFiles} files {totalFolders > 0 && `in ${totalFolders} folders`}
        </span>
      </div>
      <div className="file-tree-content" role="tree" aria-label="File tree">
        {files.length === 0 ? (
          <div className="file-tree-empty" data-testid="file-tree-empty">
            <span className="empty-icon">📭</span>
            <p>No files generated yet</p>
            <span className="empty-hint">Files will appear here after build starts</span>
          </div>
        ) : (
          renderTree(fileTree)
        )}
      </div>
    </div>
  );
}

FileTree.propTypes = {
  /** Array of file objects with path, size, status */
  files: PropTypes.arrayOf(
    PropTypes.shape({
      path: PropTypes.string.isRequired,
      size: PropTypes.number,
      status: PropTypes.oneOf(['generated', 'pending', 'error', 'modified']),
    })
  ),
  /** Callback when file is selected */
  onFileSelect: PropTypes.func,
  /** Currently selected file path */
  selectedFile: PropTypes.string,
  /** Expand all folders by default */
  defaultExpanded: PropTypes.bool,
  /** Show file count in folder labels */
  showFileCount: PropTypes.bool,
  /** Maximum tree depth to render */
  maxDepth: PropTypes.number,
};

export default FileTree;
