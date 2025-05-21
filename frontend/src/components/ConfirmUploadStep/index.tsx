'use client'
import { FC } from 'react'
import { UploadedFile } from '@/types/UploadedFile'
import { DoubleButton } from '../DoubleButton'
import { FileHeader } from '../FileHeader'

type ConfirmUploadStepProps = {
  file: UploadedFile;
  onReset: () => void;
  onConfirm: () => void;
}


export const ConfirmUploadStep: FC< ConfirmUploadStepProps > = ({ file, onReset, onConfirm }) => {
  return (
    <div data-testid="confirm-upload-step">
      <FileHeader file={file} />
      <label className='group flex cursor-pointer gap-2 rounded-xl border-2 border-blue-200 bg-blue-25 p-4'>
        <div>
          <div className='grid size-4 place-items-center rounded-full border border-blue-600'>
            <div className='h-2 w-2 rounded-full bg-blue-600 transition-opacity'></div>
          </div>
        </div>
        <div className='flex flex-col gap-0.5'>
          <span className='text-sm leading-4 text-blue-800'>
            Convert to PDF
          </span>
          <span className='text-sm text-blue-700'>
            Best quality, retains images and other assets.
          </span>
        </div>
      </label>
      <DoubleButton 
        leftText={'Cancel'}
        rightText={'Convert'}
        onLeft={onReset}
        onRight={onConfirm}
      />
    </div>
  )
}