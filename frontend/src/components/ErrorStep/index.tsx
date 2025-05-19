import { FC } from "react"

type ErrorStepProps = {
  onReset: () => void;
}

export const ErrorStep: FC<ErrorStepProps> = ({onReset}) => {
  return (
    <div className="flex w-full flex-col items-center gap-1 rounded-lg border border-gray-300 p-4 text-center" data-testid="error-step">
      <p className="text-lg font-semibold text-red-600" data-testid="error-message">
        An error has occurred
      </p>
      <button 
        onClick={onReset}
        className="rounded-lg bg-blue-600 px-4 py-2.5 text-white"
        data-testid="retry-button"
      >
        Try again
      </button>
    </div>
  )
}