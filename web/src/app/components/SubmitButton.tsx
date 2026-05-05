'use client';

import { motion } from 'framer-motion';
import { Sparkles } from 'lucide-react';

interface Props {
  loading: boolean;
  disabled: boolean;
  onClick: () => void;
}

export default function SubmitButton({ loading, disabled, onClick }: Props) {
  return (
    <motion.button
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.25 }}
      whileHover={!disabled ? { scale: 1.02, y: -1 } : {}}
      whileTap={!disabled ? { scale: 0.98 } : {}}
      onClick={onClick}
      disabled={disabled}
      className="w-full py-4 rounded-2xl font-bold text-lg transition-all duration-300 flex items-center justify-center gap-2"
      style={{
        background: disabled
          ? '#e8e4da'
          : 'linear-gradient(135deg, #ff6b6b 0%, #ffa07a 50%, #a78bfa 100%)',
        backgroundSize: '200% 200%',
        color: disabled ? '#b0aca4' : '#ffffff',
        boxShadow: disabled
          ? 'none'
          : '0 4px 20px rgba(255, 107, 107, 0.3), 0 2px 8px rgba(167, 139, 250, 0.2)',
        cursor: disabled ? 'not-allowed' : 'pointer',
      }}
    >
      {loading ? (
        <>
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}
          >
            <Sparkles size={22} />
          </motion.div>
          <span>生成中...</span>
        </>
      ) : (
        <>
          <Sparkles size={22} />
          <span>生成动漫视频</span>
        </>
      )}
    </motion.button>
  );
}
