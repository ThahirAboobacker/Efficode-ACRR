// src/components/CodeEditor/index.tsx
import React, { useRef, useEffect } from 'react';
import Editor from "@monaco-editor/react";
import './styles.css';

interface CodeEditorProps {
  code: string;
  onChange: (value: string) => void;
  language?: string;
  readOnly?: boolean;
  highlightDiff?: boolean;
  originalCode?: string;
}

const CodeEditor: React.FC<CodeEditorProps> = ({ 
  code, 
  onChange, 
  language = "python", 
  readOnly = false,
  highlightDiff = false,
  originalCode
}) => {
  const editorRef = useRef<any>(null);
  
  // Handle editor mounting
  const handleEditorDidMount = (editor: any) => {
    editorRef.current = editor;
  };
  
  // Highlight differences when needed
  useEffect(() => {
    if (highlightDiff && editorRef.current && originalCode) {
      try {
        // Simple line-based diff highlighting
        const originalLines = originalCode.split('\n');
        const newLines = code.split('\n');
        
        const decorations: any[] = [];
        
        // Find changed lines (very simple approach)
        newLines.forEach((line, i) => {
          if (i < originalLines.length && line !== originalLines[i]) {
            decorations.push({
              range: new (window as any).monaco.Range(i+1, 1, i+1, 1),
              options: {
                isWholeLine: true,
                className: 'modified-line',
                linesDecorationsClassName: 'modified-line-gutter'
              }
            });
          }
        });
        
        editorRef.current.deltaDecorations([], decorations);
      } catch (err) {
        console.error("Failed to highlight differences:", err);
      }
    }
  }, [code, originalCode, highlightDiff]);

  return (
    <div className="code-editor-container">
      <Editor
        height="400px"
        defaultLanguage={language}
        language={language}
        value={code}
        theme="vs-dark"
        onChange={(value) => onChange(value || '')}
        options={{
          minimap: { enabled: false },
          fontSize: 14,
          readOnly,
          scrollBeyondLastLine: false,
          automaticLayout: true,
          lineNumbers: 'on',
          folding: true,
          tabSize: 4,
          wordWrap: 'on',
          padding: { top: 10 }
        }}
        onMount={handleEditorDidMount}
        className="editor"
      />
    </div>
  );
};

export default CodeEditor;