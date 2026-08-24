import unittest

from app.phase2 import parse_requirement_text, public_ai_answer


class PublicAiAnswerTest(unittest.TestCase):
    def test_keeps_normal_final_answer(self):
        self.assertEqual(public_ai_answer('支持船舶检测算法。', 'fallback'), '支持船舶检测算法。')

    def test_removes_think_block(self):
        self.assertEqual(
            public_ai_answer('<think>internal reasoning</think>支持船舶检测算法。', 'fallback'),
            '支持船舶检测算法。',
        )

    def test_rejects_reasoning_only_response(self):
        leaked = "Here's a thinking process: 1. Analyze User Input 2. Final Output Generation"
        self.assertEqual(public_ai_answer(leaked, '结构化事实答案'), '结构化事实答案')

    def test_extracts_explicit_final_answer(self):
        self.assertEqual(
            public_ai_answer('分析内容\nFinal Answer: 支持船舶检测算法。', 'fallback'),
            '支持船舶检测算法。',
        )


class RequirementParserTest(unittest.TestCase):
    def test_shared_upstream_and_downstream_distance(self):
        parsed = parse_requirement_text(
            '某桥梁上下游各3公里，需要4个球机，需要AIS融合、船名OCR、偏航预警，7×24小时运行。'
        )
        self.assertEqual(parsed['upstreamKm'], 3)
        self.assertEqual(parsed['downstreamKm'], 3)
        self.assertEqual(parsed['ptzCount'], 4)

    def test_separate_upstream_and_downstream_distances(self):
        parsed = parse_requirement_text('桥梁上游2公里、下游5公里，需要2个球机。')
        self.assertEqual(parsed['upstreamKm'], 2)
        self.assertEqual(parsed['downstreamKm'], 5)


if __name__ == '__main__':
    unittest.main()
