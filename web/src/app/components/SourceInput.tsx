'use client';

import { motion } from 'framer-motion';
import { fadeUp } from './animations';
import type { SourceType, SceneMode } from './types';
import { INPUT_TABS } from './constants';

interface Props {
  source: string;
  sourceType: SourceType;
  sceneMode: SceneMode;
  onChange: (source: string) => void;
  onTypeChange: (type: SourceType) => void;
}

function getPlaceholder(type: SourceType, scene: SceneMode): string {
  if (scene === 'news') {
    if (type === 'web_link') return '粘贴新闻链接...\n例如：https://news.example.com/...';
    if (type === 'text') return '输入或粘贴新闻内容...\n例如：今日股市大涨3%，科技板块领涨...';
    return '粘贴新闻相关内容...';
  }
  if (scene === 'dialogue') {
    if (type === 'douyin_video') return '粘贴抖音对话视频链接...\n例如：https://v.douyin.com/xxxxx';
    if (type === 'text') return '输入对话内容...\n例如：\n甲：今天天气真好！\n乙：是啊，我们去野餐吧！';
    return '粘贴对话相关内容...';
  }
  if (type === 'text') return '输入你想改编的内容...\n支持文字、链接、视频URL';
  if (type === 'web_link') return '粘贴网页链接...';
  if (type === 'douyin_video') return '粘贴抖音视频链接...';
  return '上传或粘贴内容...';
}

export default function SourceInput({ source, sourceType, sceneMode, onChange, onTypeChange }: Props) {
  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={fadeUp}
      transition={{ delay: 0.15 }}
      className="mb-8 rounded-2xl p-6"
      style={{
        background: '#ffffff',
        border: '1px solid #f0e6d8',
        boxShadow: '0 1px 3px rgba(45,45,45,0.04), 0 1px 2px rgba(45,45,45,0.02)',
      }}
    >
      {/* Input Type Tabs — Pill style */}
      <div className="flex gap-2 mb-4 flex-wrap">
        {INPUT_TABS.map(({ type, icon: Icon, label }) => {
          const isActive = sourceType === type;
          return (
            <motion.button
              key={type}
              onClick={() => onTypeChange(type)}
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              className="flex items-center gap-1.5 px-4 py-2 rounded-pill text-sm font-medium transition-all duration-200"
              style={{
                background: isActive
                  ? 'linear-gradient(135deg, #ff6b6b, #ffa07a, #a78bfa)'
                  : '#fef9f0',
                color: isActive ? '#ffffff' : '#5f5f5d',
                border: isActive ? 'none' : '1px solid #f0e6d8',
                boxShadow: isActive
                  ? '0 2px 8px rgba(255, 107, 107, 0.25)'
                  : 'none',
              }}
            >
              <Icon size={15} />
              {label}
            </motion.button>
          );
        })}
      </div>

      {/* Textarea */}
      <textarea
        value={source}
        onChange={(e) => onChange(e.target.value)}
        placeholder={getPlaceholder(sourceType, sceneMode)}
        className="w-full h-36 p-4 rounded-xl resize-none text-base leading-relaxed transition-all duration-200"
        style={{
          background: '#fef9f0',
          border: '1px solid #f0e6d8',
          color: '#2d2d2d',
          outline: 'none',
        }}
        onFocus={(e) => {
          e.target.style.borderColor = '#a78bfa';
          e.target.style.boxShadow = '0 0 0 3px rgba(167, 139, 250, 0.12)';
        }}
        onBlur={(e) => {
          e.target.style.borderColor = '#f0e6d8';
          e.target.style.boxShadow = 'none';
        }}
      />
    </motion.div>
  );
}
