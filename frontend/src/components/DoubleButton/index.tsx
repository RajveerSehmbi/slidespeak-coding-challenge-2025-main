'use client'
import { FC } from 'react'

type DoubleButtonProps = {
    leftText: string;
    rightText: string;
    onLeft: () => void;
    onRight: () => void;
};

export const DoubleButton: FC< DoubleButtonProps > = ({leftText, rightText, onLeft, onRight}) => {

    return (
        <div className='flex w-full gap-3'>
          <button
          onClick={onLeft} 
          className='w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 font-semibold text-gray-700 shadow-sm disabled:cursor-not-allowed disabled:opacity-30'
          data-testid="left-button"
          >
            {leftText}
          </button>
          <button
          onClick={onRight}
          className='flex w-full items-center justify-center rounded-lg border border-blue-600 bg-blue-600 px-4 py-2.5 font-semibold text-white shadow-sm disabled:cursor-not-allowed disabled:opacity-30'
          data-testid="right-button"
          >
            {rightText}
          </button>
        </div>
    );
}