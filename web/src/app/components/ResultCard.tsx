'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Download, RotateCcw } from 'lucide-react';

interface Props {
  result: string | null;
  onReset: () => void;
}

export default function ResultCard({ result, onReset }: Props) {
  return (
    <AnimatePresence>
      {result && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          className="mt-8 rounded-2xl p-6"
          style={{
            background: '#ffffff',
            border: '1px solid #f0e6d8',
            boxShadow: '0 4px 24px rgba(45,45,45,0.06)',
          }}
        >
          <div className="flex items-center gap-2 mb-4">
            <div
              className="w-8 h-8 rounded-full flex items-center justify-center"
              style={{ background: 'linear-gradient(135deg, #ff6b6b, #a78bfa)' }}
            >
              <Sparkles size={16} className="text-white" />
            </div>
            <h3 className="text-lg font-semibold" style={{ color: '#2d2d2d' }}>
              生成完成！
            </h3>
          </div>

          <video
            src={result}
            controls
            className="w-full rounded-xl"
            style={{ background: '#1a1a1a' }}
            poster="/placeholder-thumb.jpg"
          />

          <div className="flex gap-3 mt-4">
            <a
              href={result}
              download
              className="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl font-semibold text-sm transition-all duration-200"
              style={{
                background: 'linear-gradient(135deg, #ff6b6b, #ffa07a)',
                color: '#ffffff',
                boxShadow: '0 2px 8px rgba(255, 107, 107, 0.25)',
              }}
            >
              <Download size={17} />
              下载视频
            </a>
            <button
              onClick={onReset}
              className="flex items-center justify-center gap-2 py-3 px-6 rounded-xl font-semibold text-sm transition-all duration-200 hover:opacity-80"
              style={{
                background: '#fef9f0',
                color: '#5f5f5d',
                border: '1px solid #f0e6d8',
              }}
            >
              <RotateCcw size={17} />
              再来一次
            </button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
