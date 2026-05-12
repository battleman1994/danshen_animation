import json
import pytest
from src.pipeline.storyboard import Storyboard, StoryboardScene


class TestStoryboardScene:
    def test_create_valid_scene(self):
        scene = StoryboardScene(
            index=1, duration_s=4, dialogue="今天天气真好",
            character="tabby_cat", emotion="happy",
            action="waving_paw", background="sunny_park",
            camera="medium_shot",
        )
        assert scene.index == 1
        assert scene.duration_s == 4
        assert scene.dialogue == "今天天气真好"
        assert scene.emotion == "happy"

    def test_to_dict_roundtrip(self):
        scene = StoryboardScene(
            index=1, duration_s=4, dialogue="你好",
            character="tabby_cat", emotion="funny",
        )
        data = scene.to_dict()
        restored = StoryboardScene.from_dict(data)
        assert restored.index == scene.index
        assert restored.duration_s == scene.duration_s
        assert restored.dialogue == scene.dialogue
        assert restored.emotion == scene.emotion

    def test_invalid_duration(self):
        with pytest.raises(ValueError, match="duration_s"):
            StoryboardScene(
                index=1, duration_s=1, dialogue="hi",
                character="tabby_cat",
            )

    def test_invalid_emotion(self):
        with pytest.raises(ValueError, match="emotion"):
            StoryboardScene(
                index=1, duration_s=4, dialogue="hi",
                character="tabby_cat", emotion="unknown",
            )

    def test_invalid_camera(self):
        with pytest.raises(ValueError, match="camera"):
            StoryboardScene(
                index=1, duration_s=4, dialogue="hi",
                character="tabby_cat", camera="extreme_close",
            )

    def test_default_values(self):
        scene = StoryboardScene(
            index=1, duration_s=4, dialogue="hello",
            character="panda",
        )
        assert scene.emotion == "neutral"
        assert scene.camera == "medium_shot"
        assert scene.background == "simple_studio"


class TestStoryboard:
    def test_create_valid_storyboard(self):
        scenes = [
            StoryboardScene(index=1, duration_s=4, dialogue="你好", character="tabby_cat", emotion="happy"),
            StoryboardScene(index=2, duration_s=4, dialogue="你好呀", character="tabby_cat", emotion="happy"),
        ]
        sb = Storyboard(scenes=scenes, total_duration_s=8, style="funny")
        assert len(sb.scenes) == 2
        assert sb.total_duration_s == 8
        assert sb.style == "funny"

    def test_auto_compute_total_duration(self):
        scenes = [
            StoryboardScene(index=1, duration_s=4, dialogue="line1", character="tabby_cat"),
            StoryboardScene(index=2, duration_s=5, dialogue="line2", character="tabby_cat"),
        ]
        sb = Storyboard(scenes=scenes, total_duration_s=0, style="funny")
        assert sb.total_duration_s == 9

    def test_no_scenes_raises(self):
        with pytest.raises(ValueError, match="at least"):
            Storyboard(scenes=[], total_duration_s=0, style="funny")

    def test_duration_too_long(self):
        with pytest.raises(ValueError, match="must be 2-8"):
            StoryboardScene(index=1, duration_s=65, dialogue="long", character="tabby_cat")

    def test_invalid_style(self):
        with pytest.raises(ValueError, match="style"):
            Storyboard(
                scenes=[StoryboardScene(index=1, duration_s=3, dialogue="hi", character="tabby_cat")],
                total_duration_s=3, style="horror",
            )

    def test_to_json(self):
        scenes = [
            StoryboardScene(index=1, duration_s=4, dialogue="你好", character="tabby_cat", emotion="happy"),
        ]
        sb = Storyboard(scenes=scenes, total_duration_s=4, style="funny")
        json_str = sb.to_json()
        data = json.loads(json_str)
        assert len(data["scenes"]) == 1
        assert data["scenes"][0]["dialogue"] == "你好"

    def test_from_dict_roundtrip(self):
        scenes = [
            StoryboardScene(index=1, duration_s=4, dialogue="hello", character="panda", emotion="funny"),
            StoryboardScene(index=2, duration_s=3, dialogue="world", character="panda", emotion="surprised"),
        ]
        sb = Storyboard(scenes=scenes, total_duration_s=7, style="cute")
        restored = Storyboard.from_dict(sb.to_dict())
        assert restored.total_duration_s == 7
        assert restored.style == "cute"
        assert len(restored.scenes) == 2
        assert restored.scenes[0].dialogue == "hello"
        assert restored.scenes[1].emotion == "surprised"
