/**
 * Danshen Animation — 共享类型定义
 * 前端和后端通用类型约束
 */

// ── 内容输入类型 ──
export type SourceType =
  | 'text'
  | 'douyin_video'
  | 'bilibili_video'
  | 'youtube_video'
  | 'web_link'
  | 'image'
  | 'weibo_post';

// ── 角色 ID ──
export type CharacterId =
  | 'tabby_cat'
  | 'brown_bear'
  | 'little_fox'
  | 'panda'
  | 'rabbit'
  | 'shiba_inu'
  | 'owl'
  | 'penguin'
  | 'lion';

// ── 生成风格 ──
export type AnimationStyle = 'auto' | 'funny' | 'serious' | 'cute' | 'news';

// ── 新闻严重度 ──
export type NewsSeverity = 'entertainment' | 'social' | 'finance_tech' | 'major_event';

// ── API 请求 ──
export interface AnimateRequest {
  source: string;
  source_type: SourceType;
  character?: CharacterId;
  character_count?: number;
  style?: AnimationStyle;
  resolution?: '720p' | '1080p';
  subtitle?: boolean;
  webhook_url?: string | null;
  // 场景模式
  scene_mode?: 'dialogue' | 'news_broadcast' | 'auto';
}

export interface AnimateResponse {
  task_id: string;
  status: 'queued';
  estimated_time: number;
  poll_url: string;
}

// ── 任务状态 ──
export type TaskStatus = 'queued' | 'extracting' | 'adapting' | 'generating_characters' | 'synthesizing_voice' | 'composing_video' | 'completed' | 'failed';

export interface TaskResult {
  video_url: string;
  video_path: string;
  duration: number;
}

export interface TaskStatusResponse {
  task_id: string;
  status: TaskStatus;
  progress: number;
  result: TaskResult | null;
  error: string | null;
}

// ── 角色信息 ──
export interface CharacterInfo {
  id: CharacterId;
  name: string;
  emoji: string;
  style: string;
}

// ── 新闻分析结果 ──
export interface AnimalAnchor {
  animal_id: CharacterId;
  name: string;
  emoji: string;
  voice_id: string;
  broadcast_tone: string;
}

export interface NewsAnalysisResult {
  severity: NewsSeverity;
  severity_label: string;
  confidence: number;
  anchor: AnimalAnchor;
  summary: string;
  keywords: string[];
  suggested_title: string;
}

// ── 角色库 ──
export const CHARACTERS: CharacterInfo[] = [
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

// ── 新闻分级 → 动物映射 ──
export const NEWS_ANIMAL_MAP: Record<NewsSeverity, AnimalAnchor> = {
  entertainment: { animal_id: 'shiba_inu', name: '柴犬主播', emoji: '🐕', voice_id: 'zh-CN-XiaoxiaoNeural', broadcast_tone: '轻松调侃' },
  social: { animal_id: 'owl', name: '猫头鹰主播', emoji: '🦉', voice_id: 'zh-CN-YunxiNeural', broadcast_tone: '温和稳重' },
  finance_tech: { animal_id: 'penguin', name: '企鹅主播', emoji: '🐧', voice_id: 'zh-CN-YunyangNeural', broadcast_tone: '严谨专业' },
  major_event: { animal_id: 'lion', name: '雄狮主播', emoji: '🦁', voice_id: 'zh-CN-YunxiNeural', broadcast_tone: '庄重严肃' },
};
