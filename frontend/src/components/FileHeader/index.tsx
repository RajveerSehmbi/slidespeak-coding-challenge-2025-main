import { FC } from "react"
import { UploadedFile } from "@/types/UploadedFile"


type FileHeaderProps = {
    file: UploadedFile
}

export const FileHeader: FC< FileHeaderProps > = ({file}) => {
    return (
        <div className='flex w-full flex-col gap-1 rounded-lg border border-gray-300 p-4 text-center' data-testid="file-header">
            <p className='text-lg font-semibold text-gray-800'>
                {file.name}
            </p>
            <p className='text-sm text-gray-600' data-testid="file-size">
              {(file.size / 1024 / 1024).toFixed(2)} MB
            </p>
        </div>
    )
}