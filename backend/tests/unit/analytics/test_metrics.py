def test_every_analyzer_returns_score_in_range(sample_frame):
    from analytics.metrics.composure_analyzer import ComposureAnalyzer
    from analytics.metrics.engagement_analyzer import EngagementAnalyzer
    from analytics.metrics.focus_analyzer import FocusAnalyzer
    from analytics.metrics.posture_analyzer import PostureAnalyzer
    from analytics.metrics.presence_analyzer import PresenceAnalyzer

    frames = [sample_frame(), sample_frame(0.005), sample_frame(0.01)]
    analyzers = [
        FocusAnalyzer(),
        PostureAnalyzer(),
        EngagementAnalyzer(),
        PresenceAnalyzer(),
        ComposureAnalyzer(),
    ]

    for analyzer in analyzers:
        score = analyzer.analyze(frames)
        assert score is not None, analyzer.__class__.__name__
        assert 0 <= score <= 100, analyzer.__class__.__name__
