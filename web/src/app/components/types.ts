// Shared types for danshen_animation web UI

export type SceneMode = 'auto' | 'dialogue' | 'news';
export type SourceType = 'text' | 'web_link' | 'image' | 'douyin_video';

export interface Character {
  id: string;
  name: string;
  emoji: string;
  style: string;
}

export interface Scene {
  id: SceneMode;
  name: string;
  icon: React.ComponentType<{ size?: number | string; className?: string; style?: React.CSSProperties }>;
  desc: string;
}

export interface InputTab {
  type: SourceType;
  icon: React.ComponentType<{ size?: number | string; className?: string; style?: React.CSSProperties }>;
  label: string;
}

export interface Style {
  id: string;
  label: string;
}
