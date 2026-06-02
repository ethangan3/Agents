import mini_agent.tools.weather_search as weather_search


def test_search_returns_error_when_api_key_missing(monkeypatch):
    monkeypatch.delenv("SERPAPI_API_KEY", raising=False)

    class FailingClient:
        def __init__(self, params):
            raise AssertionError("SerpApiClient should not be created")

    monkeypatch.setattr(weather_search, "SerpApiClient", FailingClient)

    result = weather_search.search("北京天气")

    assert "SERPAPI_API_KEY" in result


def test_search_prefers_answer_box_list(monkeypatch):
    monkeypatch.setenv("SERPAPI_API_KEY", "fake-key")

    class FakeClient:
        def __init__(self, params):
            self.params = params

        def get_dict(self):
            return {"answer_box_list": ["第一条", "第二条"]}

    monkeypatch.setattr(weather_search, "SerpApiClient", FakeClient)

    result = weather_search.search("问题")

    assert result == "第一条\n第二条"


def test_search_prefers_answer_box_answer(monkeypatch):
    monkeypatch.setenv("SERPAPI_API_KEY", "fake-key")

    class FakeClient:
        def __init__(self, params):
            self.params = params

        def get_dict(self):
            return {"answer_box": {"answer": "直接答案"}}

    monkeypatch.setattr(weather_search, "SerpApiClient", FakeClient)

    result = weather_search.search("问题")

    assert result == "直接答案"


def test_search_uses_knowledge_graph_description(monkeypatch):
    monkeypatch.setenv("SERPAPI_API_KEY", "fake-key")

    class FakeClient:
        def __init__(self, params):
            self.params = params

        def get_dict(self):
            return {"knowledge_graph": {"description": "知识图谱描述"}}

    monkeypatch.setattr(weather_search, "SerpApiClient", FakeClient)

    result = weather_search.search("问题")

    assert result == "知识图谱描述"


def test_search_falls_back_to_top_three_organic_snippets(monkeypatch):
    monkeypatch.setenv("SERPAPI_API_KEY", "fake-key")

    class FakeClient:
        def __init__(self, params):
            self.params = params

        def get_dict(self):
            return {
                "organic_results": [
                    {"title": "标题1", "snippet": "摘要1"},
                    {"title": "标题2", "snippet": "摘要2"},
                    {"title": "标题3", "snippet": "摘要3"},
                    {"title": "标题4", "snippet": "摘要4"},
                ]
            }

    monkeypatch.setattr(weather_search, "SerpApiClient", FakeClient)

    result = weather_search.search("问题")

    assert "[1] 标题1" in result
    assert "[3] 标题3" in result
    assert "标题4" not in result


def test_search_returns_not_found_message_when_no_supported_result(monkeypatch):
    monkeypatch.setenv("SERPAPI_API_KEY", "fake-key")

    class FakeClient:
        def __init__(self, params):
            self.params = params

        def get_dict(self):
            return {}

    monkeypatch.setattr(weather_search, "SerpApiClient", FakeClient)

    result = weather_search.search("不存在的问题")

    assert "没有找到" in result
    assert "不存在的问题" in result


def test_search_catches_client_exception(monkeypatch):
    monkeypatch.setenv("SERPAPI_API_KEY", "fake-key")

    class FakeClient:
        def __init__(self, params):
            self.params = params

        def get_dict(self):
            raise RuntimeError("network failed")

    monkeypatch.setattr(weather_search, "SerpApiClient", FakeClient)

    result = weather_search.search("问题")

    assert "搜索时发生错误" in result
    assert "network failed" in result
