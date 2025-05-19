'use client'
import { FC, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import UploadIcon from '@/icons/UploadIcon';
import { UploadedFile } from '@/types/UploadedFile';


type ChooseFileStepProps = {
  onFileAccepted: (file: UploadedFile) => void;
};

export const ChooseFileStep: FC<ChooseFileStepProps> = ({ onFileAccepted }) => {
  
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles && acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      onFileAccepted({
        name: file.name,
        size: file.size,
        type: file.type,
        fileObj: file
      });
    }
  }, [onFileAccepted]);

  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.ms-powerpoint': ['.ppt'],
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx']
    }
  });

  return (
    <div
      className="group cursor-pointer rounded-xl border border-dashed border-gray-400 bg-white px-6 py-16"
      {...getRootProps()}
      data-testid="choose-file-step"
    >
      <input {...getInputProps()} data-testid="file-input"/>
      <div className="flex shrink-0 grow-0 flex-col items-center gap-2">
        <div className="mb-2 rounded-full bg-gray-100 p-2">
          <div className="grid place-items-center rounded-full bg-gray-200 p-2 [&>svg]:size-8">
            <UploadIcon />
          </div>
        </div>
        <p className="text-sm leading-8 text-gray-600" data-testid="upload_instructions">
          Drag and drop a PowerPoint file to convert to PDF.
        </p>
        <button
          type="button"
          className="rounded-lg bg-blue-50 px-4 py-2.5 text-sm text-blue-700 transition-colors group-hover:bg-blue-100"
          data-testid="choose-file-button"
        >
          Choose file
        </button>
      </div>
    </div>
  );
};
