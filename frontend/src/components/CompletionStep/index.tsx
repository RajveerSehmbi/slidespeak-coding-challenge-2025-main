import { PdfIcon } from "@/icons/PdfIcon"
import { FC } from "react"
import { DoubleButton } from "../DoubleButton"

type CompletionStepProps = {
  onReset: () => void;
  onDownload: () => void;
}

export const CompletionStep: FC<CompletionStepProps> = ({onReset, onDownload}) => {

    return (
      <div data-testid="completion-step">
        <div className="flex w-full flex-col items-center gap-1 rounded-lg border border-gray-300 p-4 text-center">
          <PdfIcon/>
          <p className="text-lg font-semibold text-gray-800" data-testid="success-message">
            File converted successfully!
          </p>
        </div>
        <DoubleButton
          leftText={'Convert another'}
          rightText={'Download file'}
          onLeft={onReset}
          onRight={onDownload}
        />
      </div>
    )
}