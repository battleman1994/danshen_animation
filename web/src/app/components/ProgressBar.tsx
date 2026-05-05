'use client';

import { motion, AnimatePresence } from 'framer-motion';

interface Props {
  loading: boolean;
  progress: number;
  statusText: string;
}

export default function ProgressBar({ loading, progress, statusText }: Props) {
  return (
    <AnimatePresence>
      {loading && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          className="mt-6 rounded-2xl p-5"
          style={{
            background: '#ffffff',
            border: '1px solid #f0e6d8',
            boxShadow: '0 1px 3px rgba(45,45,45,0.04)',
          }}
        >
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium" style={{ color: '#5f5f5d' }}>
              {statusText}
            </span>
            <span className="text-sm font-bold" style={{ color: '#a78bfa' }}>
              {progress}%
            </span>
          </div>
          <div className="w-full rounded-full h-2.5" style={{ background: '#fef9f0' }}>
            <motion.div
              className="h-2.5 rounded-full"
              style={{
                background: 'linear-gradient(90deg, #ff6b6b, #ffa07a, #a78bfa)',
                backgroundSize: '200% 100%',
              }}
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5, ease: 'easeOut' }}
            />
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
