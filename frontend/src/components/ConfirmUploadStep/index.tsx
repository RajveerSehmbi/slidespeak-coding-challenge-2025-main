'use client'
import { FC } from 'react'
import { UploadedFile } from '@/types/UploadedFile'
import { DoubleButton } from '../DoubleButton'
import { ConversionList } from '../ConversionList'
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
      <ConversionList />
      <DoubleButton 
        leftText={'Cancel'}
        rightText={'Convert'}
        onLeft={onReset}
        onRight={onConfirm}
      />
    </div>
  )
}