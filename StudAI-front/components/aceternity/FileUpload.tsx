'use client';

import { cn } from '@/lib/utils';
import React, { useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { IconUpload } from '@tabler/icons-react';
import { useDropzone } from 'react-dropzone';

const mainVariant = {
  initial: {
    x: 0,
    y: 0,
  },
  animate: {
    x: 20,
    y: -20,
    opacity: 0.9,
  },
};

const secondaryVariant = {
  initial: {
    opacity: 0,
  },
  animate: {
    opacity: 1,
  },
};

export const FileUpload = ({
  onChange,
}: {
  onChange?: (files: File[]) => void;
}) => {
  const [files, setFiles] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (newFiles: File[]) => {
    setFiles(newFiles);
    onChange && onChange(newFiles);
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const { getRootProps, isDragActive } = useDropzone({
    multiple: false,
    noClick: true,
    onDrop: handleFileChange,
    onDropRejected: (error) => {
      console.log(error);
    },
    accept: {
      'application/pdf': ['.pdf'],
    },
  });

  return (
    <div className="w-full" {...getRootProps()}>
      <motion.div
        onClick={handleClick}
        whileHover="animate"
        className="group/file block rounded-lg cursor-pointer w-full relative overflow-hidden"
      >
        <input
          ref={fileInputRef}
          id="file-upload-handle"
          type="file"
          accept=".pdf"
          onChange={(e) => handleFileChange(Array.from(e.target.files || []))}
          className="hidden"
        />
        <div className="relative w-full">
          <div
            className={cn(
              'relative z-40 bg-black/40 backdrop-blur-md border border-white/10 rounded-2xl p-10 transition-all duration-300',
              isDragActive && 'border-white/30 bg-black/60'
            )}
          >
            <div className="flex flex-col items-center justify-center">
              <div className="relative w-full mt-10 max-w-xl mx-auto">
                {files.length > 0 ? (
                  <div className="flex flex-col items-center">
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="flex items-center gap-3 bg-white/5 border border-white/10 rounded-xl px-6 py-4 mb-4"
                    >
                      <svg
                        className="w-8 h-8 text-red-400"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fillRule="evenodd"
                          d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 0h8v12H6V4z"
                        />
                      </svg>
                      <div className="flex-1">
                        <p className="text-white font-medium">
                          {files[0].name}
                        </p>
                        <p className="text-white/50 text-sm">
                          {(files[0].size / 1024).toFixed(1)} KB
                        </p>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setFiles([]);
                          onChange && onChange([]);
                        }}
                        className="text-white/60 hover:text-white transition-colors"
                      >
                        <svg
                          className="w-5 h-5"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M6 18L18 6M6 6l12 12"
                          />
                        </svg>
                      </button>
                    </motion.div>
                  </div>
                ) : (
                  <motion.div
                    layoutId="file-upload"
                    variants={mainVariant}
                    transition={{
                      type: 'spring',
                      stiffness: 300,
                      damping: 20,
                    }}
                    className="relative group-hover/file:shadow-2xl z-40 bg-white/5 flex items-center justify-center h-32 w-full max-w-[8rem] mx-auto rounded-2xl border border-white/10 backdrop-blur-sm"
                  >
                    <svg
                      className="w-10 h-10 text-white/70"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={1.5}
                        d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                      />
                    </svg>
                  </motion.div>
                )}

                {!files.length && (
                  <>
                    <motion.div
                      variants={secondaryVariant}
                      className="absolute opacity-0 border border-dashed border-white/20 inset-0 z-30 bg-transparent flex items-center justify-center h-32 w-full max-w-[8rem] mx-auto rounded-2xl"
                    ></motion.div>
                  </>
                )}
              </div>

              <div className="text-center mt-8">
                <p className="text-white/90 text-lg font-medium mb-2">
                  {files.length > 0
                    ? 'File uploaded successfully!'
                    : 'Drop your PDF here'}
                </p>
                <p className="text-white/50 text-sm">
                  {files.length > 0
                    ? 'Click to change file'
                    : 'or click to browse'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};
