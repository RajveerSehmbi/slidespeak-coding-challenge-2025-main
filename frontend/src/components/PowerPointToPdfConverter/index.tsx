'use client'
import {FC, useCallback, useState} from "react"
import { UploadedFile } from "@/types/UploadedFile";
import { UploadStage } from "@/enums/UploadStage";
import { ChooseFileStep } from "../ChooseFileStep";
import { ConfirmUploadStep } from "../ConfirmUploadStep"
import { ProcessingStep } from "../ProcessingStep";
import { CompletionStep } from "../CompletionStep";
import { ErrorStep } from "../ErrorStep";

type PowerPointToPdfConverterProps = {
};

export const PowerPointToPdfConverter: FC<PowerPointToPdfConverterProps> = () => {
  const [uploadedFile, setUploadedFile] = useState<UploadedFile | null>(null);
  const [currentStage, setCurrentStage] = useState<UploadStage>(UploadStage.CHOOSE_FILE);
  const [jobId, setJobId] = useState<string | null>(null);
  const [presignUrl, setPresignUrl] = useState<string | null>(null);
  const url = process.env.NEXT_PUBLIC_BACKEND_URL


  const handleFileAccepted = useCallback((file: UploadedFile) => {
    setUploadedFile(file);
    setCurrentStage(UploadStage.CONFIRM_UPLOAD)
  }, []);


  const resetUpload = useCallback(() => {
    setUploadedFile(null);
    setCurrentStage(UploadStage.CHOOSE_FILE)
  }, []);


  const handleUpload = useCallback( async () => {
    if (!uploadedFile) return;
    try {
        const formData = new FormData();
        formData.append('file', uploadedFile.fileObj);

        console.log(url + "/upload")
        const response = await fetch(url + "/upload", {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.message);
        }
        console.log(data.job_id)
        setJobId(data.job_id);
        setCurrentStage(UploadStage.PROCESSING);
    } catch (error: any) {
        console.error(error);
        setCurrentStage(UploadStage.ERROR);
    }
  }, [uploadedFile, url]);


  const checkCompletion = useCallback( async (): Promise<boolean> => {
    try {
        const response = await fetch(url + "/status/" + jobId);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message);
        }
        if (data.status === 'completed') {
            setPresignUrl(data.presignUrl);
            setCurrentStage(UploadStage.COMPLETED);
            return true;
        }
        return false;
    } catch (error: any) {
        console.error(error);
        setCurrentStage(UploadStage.ERROR);
        return true;
    }
  }, [url, jobId])


  const handleDownload = useCallback(() => {
    if (presignUrl) {
        window.open(presignUrl, '_blank');
    }
  }, [presignUrl]);


  switch (currentStage) {
    case UploadStage.CHOOSE_FILE:
        return <ChooseFileStep onFileAccepted={handleFileAccepted} />;
    
    case UploadStage.CONFIRM_UPLOAD:
        return (
          <div className='flex flex-col gap-4 rounded-xl bg-white p-6 shadow-md'>
            <ConfirmUploadStep
              file={uploadedFile!}
              onReset={resetUpload}
              onConfirm={handleUpload}
              />
          </div>
        )
    
    case UploadStage.PROCESSING:
        return (
            <div className='flex flex-col gap-4 rounded-xl bg-white p-6 shadow-md'>
              <ProcessingStep
                file={uploadedFile!}
                jobId={jobId!}
                pollFunction={checkCompletion}
              />
            </div>
        )
    
    case UploadStage.COMPLETED:
        return (
          <div className='flex flex-col gap-4 rounded-xl bg-white p-6 shadow-md'>
            <CompletionStep
              onReset={resetUpload}
              onDownload={handleDownload}
            />
          </div>
        )
    
    case UploadStage.ERROR:
        return (
          <div className='flex flex-col gap-4 rounded-xl bg-white p-6 shadow-md'>
            <ErrorStep
              onReset={resetUpload}
            />
          </div>
        )
    }
};