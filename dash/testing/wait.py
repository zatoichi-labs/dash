# pylint: disable=too-few-public-methods
"""Utils methods for pytest-dash such wait_for wrappers."""
import time
import traceback
import logging
from selenium.common.exceptions import WebDriverException
from dash.testing.errors import TestingTimeoutError


logger = logging.getLogger(__name__)

def until(
    wait_cond,
    timeout,
    poll=0.1,
    msg="expected condition not met within timeout",
):  # noqa: C0330
    logger.debug(
        "start wait.until with method, timeout, poll => %s %s %s",
        wait_cond,
        timeout,
        poll,
    )
    end_time = time.time() + timeout
    last_exc = None
    while True:
        if hasattr(wait_cond, 'false_exceptions'):
            try:
                res = wait_cond()
            except wait_cond.false_exceptions:
                last_exc = traceback.format_exc()
                res = False
        else:
            res = wait_cond()

        if res:
            break

        if time.time() > end_time:
            if last_exc:
                logger.error("%s\n%s", last_exc, msg)
            raise TestingTimeoutError(msg)
        time.sleep(poll)
        logger.debug("poll => %s", time.time())

    return res


def until_not(
    wait_cond,
    timeout,
    poll=0.1,
    msg="expected condition met within timeout",
):  # noqa: C0330
    logger.debug(
        "start wait.until_not method, timeout, poll => %s %s %s",
        wait_cond,
        timeout,
        poll,
    )
    end_time = time.time() + timeout
    while True:
        if hasattr(wait_cond, 'false_exceptions'):
            try:
                res = wait_cond()
            except wait_cond.false_exceptions:
                res = False
        else:
            res = wait_cond()

        if not res:
            break

        if time.time() > end_time:
            raise TestingTimeoutError(msg)
        time.sleep(poll)
        logger.debug("poll => %s", time.time())

    return res


class contains_text(object):
    false_exceptions = (WebDriverException,)

    def __init__(self, selector, text):
        self.selector = selector
        self.text = text

    def __call__(self, driver):
        elem = driver.find_element_by_css_selector(self.selector)
        logger.debug(
            "contains text {%s} => expected %s", elem.text, self.text
        )
        return self.text in str(elem.text) or self.text in str(
            elem.get_attribute("value")
        )


class text_to_equal(object):
    false_exceptions = (WebDriverException,)

    def __init__(self, selector, text):
        self.selector = selector
        self.text = text

    def __call__(self, driver):
        elem = driver.find_element_by_css_selector(self.selector)
        logger.debug(
            "text to equal {%s} => expected %s", elem.text, self.text
        )
        return (
            str(elem.text) == self.text
            or str(elem.get_attribute("value")) == self.text
        )


class style_to_equal(object):
    false_exceptions = (WebDriverException,)

    def __init__(self, selector, style, val):
        self.selector = selector
        self.style = style
        self.val = val

    def __call__(self, driver):
        elem = driver.find_element_by_css_selector(self.selector)
        val = elem.value_of_css_property(self.style)
        logger.debug("style to equal {%s} => expected %s", val, self.val)
        return val == self.val
