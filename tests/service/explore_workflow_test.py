from src.service.explore_workflow import ExploreWorkflow


class FakeUI:
    def __init__(self, *, homepage=False, terminal=False, returns_home=True):
        self.homepage = homepage
        self.terminal = terminal
        self.returns_home = returns_home
        self.frames = [object(), object()]
        self.grabs = 0
        self.esc_count = 0
        self.snapshot_count = 0

    def grap(self):
        frame = self.frames[min(self.grabs, len(self.frames) - 1)]
        self.grabs += 1
        return frame

    def is_on_homepage(self, _img):
        return self.homepage

    def snapshot(self, *, img):
        assert img is self.frames[0]
        self.snapshot_count += 1
        return self

    def match_page(self, _page):
        return self.terminal

    def esc(self):
        self.esc_count += 1
        return self

    def sleep(self, _seconds):
        return self

    def wait_back_home(self, *, timeout, interval):
        assert timeout == 5
        assert interval == 0.25
        return self.returns_home


def _workflow(ui):
    workflow = ExploreWorkflow.__new__(ExploreWorkflow)
    workflow.ui = ui
    return workflow


def test_prepare_homepage_keeps_an_existing_gameplay_frame():
    ui = FakeUI(homepage=True)

    assert _workflow(ui)._prepare_homepage() is ui.frames[0]
    assert ui.snapshot_count == 0
    assert ui.esc_count == 0


def test_prepare_homepage_closes_terminal_once_and_returns_fresh_frame():
    ui = FakeUI(terminal=True, returns_home=True)

    assert _workflow(ui)._prepare_homepage() is ui.frames[1]
    assert ui.snapshot_count == 1
    assert ui.esc_count == 1


def test_prepare_homepage_rejects_unknown_non_gameplay_screen_without_input():
    ui = FakeUI(terminal=False)

    assert _workflow(ui)._prepare_homepage() is None
    assert ui.snapshot_count == 1
    assert ui.esc_count == 0
