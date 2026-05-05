'use client';

import { motion } from 'framer-motion';
import { Newspaper } from 'lucide-react';

export default function NewsModeHint() {
  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      className="mb-8 rounded-2xl p-5"
      style={{
        background: 'linear-gradient(135deg, rgba(255, 160, 122, 0.08), rgba(167, 139, 250, 0.06))',
        border: '1px solid rgba(255, 160, 122, 0.2)',
      }}
    >
      <div className="flex items-start gap-3">
        <div
          className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 mt-0.5"
          style={{ background: 'linear-gradient(135deg, #ffa07a, #ff6b6b)' }}
        >
          <Newspaper size={18} className="text-white" />
        </div>
        <div>
          <h4 className="font-semibold mb-1.5" style={{ color: '#2d2d2d' }}>
            📰 新闻播报模式
          </h4>
          <p className="text-sm leading-relaxed" style={{ color: '#5f5f5d' }}>
            AI 会根据新闻的严肃程度自动匹配动物主播：<br />
            🟢 娱乐八卦 → 🐶 柴犬 &nbsp; 🟡 社会民生 → 🦉 猫头鹰<br />
            🟠 财经科技 → 🐧 企鹅 &nbsp; 🔴 重大事件 → 🦁 雄狮
          </p>
        </div>
      </div>
    </motion.div>
  );
}
