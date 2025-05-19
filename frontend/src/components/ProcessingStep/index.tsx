'use client'
import { FC, useEffect } from 'react'
import { UploadedFile } from '@/types/UploadedFile'
import { FileHeader } from '../FileHeader'
import { LoadingIndicatorIcon } from '@/icons/LoadingIndicatorIcon'

type ProcessingStepProps = {
  file: UploadedFile;
  jobId: string;
  pollFunction: () => Promise<boolean>;
}


export const ProcessingStep: FC< ProcessingStepProps > = ({ file, jobId, pollFunction }) => {

  useEffect(() => {
    const interval = setInterval(async () => {
        const shouldStop = await pollFunction();
        if (shouldStop) {
            clearInterval(interval);
        }
    }, 2000);

    return () => clearInterval(interval);
  }, [pollFunction]);

  return (
    <div data-testid="processing-step">
      <FileHeader file={file} />
      <div className='flex w-full items-center gap-2 rounded-xl border border-gray-300 p-4' data-testid="processing-status">
        <div className='size-7 animate-spin-pretty rounded-full border-4 border-solid border-t-blue-500'></div>
        <p>Converting your file</p>
      </div>
      <div className='flex w-full gap-3' data-testid="processing-buttons">
        <button className='w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 font-semibold text-gray-700 shadow-sm disabled: cursor-not-allowed disabled: opacity-30'>
          Cancel
        </button>
        <button className='flex w-full items-center justify-center rounded-lg border border-blue-600 bg-blue-600 px-4 py-2.5 font-semibold text-white shadow-sm disabled: cursor-not-allowed disabled: opacity-30'>
          <div className='animate-spin'>
            <LoadingIndicatorIcon/>
          </div>
        </button>
      </div>
    </div>
  )
}