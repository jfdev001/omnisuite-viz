from abc import ABC, abstractmethod
import tempfile

from omnisuite_examples.animator import Animator


class AnimatorTestMixin(ABC):
    """Testcase superclass for testing implementations of Animator.

    References:
    [1] : https://stackoverflow.com/questions/243274/how-to-unit-test-abstract-classes-extend-with-stubs
    [2] : http://xunitpatterns.com/Testcase%20Superclass.html
    [3] : https://stackoverflow.com/questions/34943878/how-should-a-python-unittest-superclass-method-reference-a-variable-in-its-cal
    """

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        return

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()
        return

    def test_animate(self):
        animator = self.make_concrete_animator()
        animator.animate()
        self.assert_animate()
        return

    @abstractmethod
    def make_concrete_animator(self) -> Animator:
        pass

    @abstractmethod
    def assert_animate(self):
        pass
