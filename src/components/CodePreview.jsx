import React, { useState, useMemo, useCallback } from 'react';
import PropTypes from 'prop-types';
import '../styles/code-preview.css';

/**
 * CodePreview Component
 * Displays syntax-highlighted code preview.
 * Supports multiple languages and line numbers.
 */
function CodePreview({
  code = '',
  language = 'javascript',
  fileName = '',
  showLineNumbers = true,
  showFileName = true,
  readOnly = true,
  onChange,
  fontSize = 13,
  theme = 'dark',
  maxLines = null,
  onCopy,
}) {
  const [copied, setCopied] = useState(false);

  // Detect language from file extension
  const detectedLanguage = useMemo(() => {
    if (language) return language;
    if (!fileName) return 'plaintext';

    const ext = fileName.split('.').pop().toLowerCase();
    const langMap = {
      js: 'javascript',
      jsx: 'javascript',
      ts: 'typescript',
      tsx: 'typescript',
      py: 'python',
      rs: 'rust',
      json: 'json',
      md: 'markdown',
      css: 'css',
      html: 'html',
      toml: 'toml',
      env: 'plaintext',
    };
    return langMap[ext] || 'plaintext';
  }, [language, fileName]);

  // Split code into lines
  const lines = useMemo(() => {
    if (!code) return [];
    return code.split('\n');
  }, [code]);

  // Syntax highlighting (basic implementation)
  const highlightCode = useCallback((line, lang) => {
    if (!line) return <span className="code-line-empty">&nbsp;</span>;

    let highlighted = line;

    // Escape HTML
    highlighted = highlighted
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');

    // Basic syntax highlighting patterns
    const patterns = {
      // Comments
      comment: /(\/\/.*$|\/\*[\s\S]*?\*\/|#.*$|<!--[\s\S]*?-->)/gm,
      // Strings
      string: /(['"`])(?:(?!\1)[^\\]|\\.)*\1/g,
      // Keywords
      keyword: /\b(const|let|var|function|return|if|else|for|while|class|import|export|from|async|await|try|catch|throw|new|this|typeof|instanceof|in|of|use|pub|fn|struct|impl|trait|match|loop|while|if|let|mut|ref|move|static|extern|crate|self|Self|mod|super|where|dyn|as|box|continue|enum|unsafe|impl|trait|type|union|yield)\b/g,
      // Numbers
      number: /\b(\d+\.?\d*|0x[a-fA-F0-9]+|0b[01]+|0o[0-7]+)\b/g,
      // Functions
      function: /\b([a-zA-Z_]\w*)(?=\s*\()/g,
      // Operators
      operator: /(=>|===|!==|==|!=|<=|>=|&&|\|\||[+\-*/%=<>!&|^~?:])/g,
      // Brackets
      bracket: /([{}[\]()])/g,
    };

    // Apply highlighting based on language
    if (['javascript', 'typescript', 'jsx', 'tsx'].includes(lang)) {
      highlighted = highlighted
        .replace(patterns.string, '<span class="token string">$&</span>')
        .replace(patterns.comment, '<span class="token comment">$&</span>')
        .replace(patterns.keyword, '<span class="token keyword">$&</span>')
        .replace(patterns.function, '<span class="token function">$1</span>')
        .replace(patterns.number, '<span class="token number">$&</span>');
    } else if (lang === 'python') {
      highlighted = highlighted
        .replace(patterns.string, '<span class="token string">$&</span>')
        .replace(patterns.comment, '<span class="token comment">$&</span>')
        .replace(patterns.keyword, '<span class="token keyword">$&</span>')
        .replace(patterns.function, '<span class="token function">$1</span>')
        .replace(patterns.number, '<span class="token number">$&</span>');
    } else if (lang === 'rust') {
      highlighted = highlighted
        .replace(patterns.string, '<span class="token string">$&</span>')
        .replace(patterns.comment, '<span class="token comment">$&</span>')
        .replace(patterns.keyword, '<span class="token keyword">$&</span>')
        .replace(patterns.function, '<span class="token function">$1</span>')
        .replace(patterns.number, '<span class="token number">$&</span>');
    } else if (lang === 'json') {
      highlighted = highlighted
        .replace(patterns.string, '<span class="token string">$&</span>')
        .replace(patterns.number, '<span class="token number">$&</span>');
    }

    return <span dangerouslySetInnerHTML={{ __html: highlighted || '&nbsp;' }} />;
  }, []);

  // Handle copy to clipboard
  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
      if (onCopy) onCopy(code);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  }, [code, onCopy]);

  // Get line count
  const lineCount = lines.length;
  const displayedLines = maxLines ? lines.slice(0, maxLines) : lines;
  const hasMoreLines = maxLines && lineCount > maxLines;

  // Get language display name
  const languageDisplay = {
    javascript: 'JavaScript',
    typescript: 'TypeScript',
    python: 'Python',
    rust: 'Rust',
    json: 'JSON',
    markdown: 'Markdown',
    css: 'CSS',
    html: 'HTML',
    toml: 'TOML',
    plaintext: 'Plain Text',
  }[detectedLanguage] || detectedLanguage;

  return (
    <div
      className={`code-preview ${theme}`}
      data-testid="code-preview"
      style={{ '--font-size': `${fontSize}px` }}
    >
      {/* Header */}
      {showFileName && (
        <div className="code-preview-header" data-testid="code-preview-header">
          <div className="code-preview-file-info">
            {fileName && (
              <>
                <span className="file-icon">{getFileIcon(fileName)}</span>
                <span className="file-name" data-testid="code-preview-filename">
                  {fileName}
                </span>
              </>
            )}
            <span className="language-badge" data-testid="code-preview-language">
              {languageDisplay}
            </span>
          </div>
          <div className="code-preview-actions">
            <span className="line-count" data-testid="code-preview-lines">
              {lineCount} lines
            </span>
            <button
              className="btn-copy"
              onClick={handleCopy}
              disabled={copied}
              data-testid="code-preview-copy"
            >
              {copied ? '✓ Copied' : '📋 Copy'}
            </button>
          </div>
        </div>
      )}

      {/* Code Content */}
      <div className="code-preview-content" data-testid="code-preview-content">
        {showLineNumbers && (
          <div className="line-numbers" aria-hidden="true" data-testid="line-numbers">
            {displayedLines.map((_, index) => (
              <div key={index} className="line-number">
                {index + 1}
              </div>
            ))}
          </div>
        )}
        <pre
          className="code-content"
          data-testid="code-content"
          style={{ tabSize: 2 }}
        >
          <code className={`language-${detectedLanguage}`}>
            {displayedLines.map((line, index) => (
              <div key={index} className="code-line" data-testid={`code-line-${index}`}>
                {highlightCode(line, detectedLanguage)}
              </div>
            ))}
          </code>
        </pre>
      </div>

      {/* More lines indicator */}
      {hasMoreLines && (
        <div className="more-lines-indicator" data-testid="more-lines-indicator">
          ... {lineCount - maxLines} more lines
        </div>
      )}

      {/* Empty state */}
      {!code && (
        <div className="code-preview-empty" data-testid="code-preview-empty">
          <span className="empty-icon">📄</span>
          <p>No code to display</p>
          <span className="empty-hint">Select a file to view its contents</span>
        </div>
      )}
    </div>
  );
}

// Helper function for file icons
function getFileIcon(fileName) {
  const ext = fileName?.split('.').pop().toLowerCase();
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
  };
  return icons[ext] || '📄';
}

CodePreview.propTypes = {
  /** Code content to display */
  code: PropTypes.string,
  /** Programming language for syntax highlighting */
  language: PropTypes.string,
  /** File name for display */
  fileName: PropTypes.string,
  /** Show line numbers */
  showLineNumbers: PropTypes.bool,
  /** Show file name in header */
  showFileName: PropTypes.bool,
  /** Make editor read-only */
  readOnly: PropTypes.bool,
  /** Callback when code changes */
  onChange: PropTypes.func,
  /** Font size in pixels */
  fontSize: PropTypes.number,
  /** Color theme: 'dark' or 'light' */
  theme: PropTypes.oneOf(['dark', 'light']),
  /** Maximum lines to display */
  maxLines: PropTypes.number,
  /** Callback when code is copied */
  onCopy: PropTypes.func,
};

export default CodePreview;
