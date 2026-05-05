import { Zap, MessageCircle, Newspaper, Type, Link, Upload, Play } from 'lucide-react';
import type { Character, Scene, InputTab, Style } from './types';

export const CHARACTERS: Character[] = [
  { id: 'tabby_cat', name: '狸花猫', emoji: '🐱', style: '活泼灵巧' },
  { id: 'brown_bear', name: '棕熊', emoji: '🐻', style: '稳重憨厚' },
  { id: 'little_fox', name: '小狐狸', emoji: '🦊', style: '机灵俏皮' },
  { id: 'panda', name: '熊猫', emoji: '🐼', style: '呆萌可爱' },
  { id: 'rabbit', name: '兔子', emoji: '🐰', style: '温柔敏捷' },
  { id: 'shiba_inu', name: '柴犬', emoji: '🐶', style: '忠诚阳光' },
  { id: 'owl', name: '猫头鹰', emoji: '🦉', style: '智慧专业' },
  { id: 'penguin', name: '企鹅', emoji: '🐧', style: '憨态可掬' },
  { id: 'lion', name: '雄狮', emoji: '🦁', style: '庄重威严' },
];

export const SCENES: Scene[] = [
  { id: 'auto', name: '智能识别', icon: Zap, desc: 'AI 自动选择最佳模式' },
  { id: 'dialogue', name: '对话剧场', icon: MessageCircle, desc: '抖音对话 → 动物演绎' },
  { id: 'news', name: '新闻播报', icon: Newspaper, desc: '热点新闻 → 动物主播' },
];

export const INPUT_TABS: InputTab[] = [
  { type: 'text', icon: Type, label: '文字' },
  { type: 'web_link', icon: Link, label: '链接' },
  { type: 'image', icon: Upload, label: '图片' },
  { type: 'douyin_video', icon: Play, label: '抖音' },
];

export const STYLES: Style[] = [
  { id: 'auto', label: '🤖 自动' },
  { id: 'funny', label: '😂 搞笑' },
  { id: 'serious', label: '🎯 严肃' },
  { id: 'cute', label: '💕 可爱' },
];

export const STATUS_LABELS: Record<string, string> = {
  queued: '⏳ 排队中...',
  extracting: '📥 正在提取内容...',
  adapting: '✍️ 正在改编脚本...',
  generating_characters: '🎨 正在生成角色...',
  synthesizing_voice: '🔊 正在合成语音...',
  composing_video: '🎬 正在合成视频...',
  completed: '✨ 生成完成！',
};
