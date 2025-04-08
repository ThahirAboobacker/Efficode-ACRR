import React from 'react';
import { styled } from '@mui/material/styles';
import { Box, Paper, Typography } from '@mui/material';
import Editor from '@monaco-editor/react';

interface CodeEditorProps {
  value: string;
  onChange?: (value: string) => void;
  language?: string;
  readOnly?: boolean;
  title?: string;
}

const EditorContainer = styled(Paper)(({ theme }) => ({
  height: '500px',
  overflow: 'hidden',
  backgroundColor: theme.palette.background.paper,
  border: `1px solid ${theme.palette.divider}`,
}));

const CodeEditor: React.FC<CodeEditorProps> = ({
  value,
  onChange,
  language = 'python',
  readOnly = false,
  title,
}) => {
  const handleEditorChange = (value: string | undefined) => {
    if (onChange && value !== undefined) {
      onChange(value);
    }
  };

  return (
    <Box sx={{ width: '100%' }}>
      {title && (
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
      )}
      <EditorContainer>
        <Editor
          height="100%"
          defaultLanguage={language}
          value={value}
          onChange={handleEditorChange}
          options={{
            readOnly,
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            fontSize: 14,
            lineNumbers: 'on',
            roundedSelection: false,
            scrollbar: {
              vertical: 'visible',
              horizontal: 'visible',
            },
            theme: 'vs-dark',
          }}
        />
      </EditorContainer>
    </Box>
  );
};

export default CodeEditor; 