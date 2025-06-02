from abc import ABC, abstractmethod

from omnisuite_examples.animator import Animator


class AnimatorTestMixin(ABC):
    """Testcase superclass for testing implementations of Animator.

    References:
    [1] : https://stackoverflow.com/questions/243274/how-to-unit-test-abstract-classes-extend-with-stubs
    [2] : http://xunitpatterns.com/Testcase%20Superclass.html
    [3] : https://stackoverflow.com/questions/34943878/how-should-a-python-unittest-superclass-method-reference-a-variable-in-its-cal
    """

    def test_animate(self):
        animator = self.make_concrete_animator()
        animator.animate(save_animation=True)
        self.assert_animate()
        self.cleanup()
        return

    @abstractmethod
    def make_concrete_animator(self) -> Animator:
        pass

    @abstractmethod
    def assert_animate(self):
        pass

    @abstractmethod
    def cleanup_animate(self):
        """Cleanup side effects of animate (e.g.,temporary files/dirs)."""
        pass
