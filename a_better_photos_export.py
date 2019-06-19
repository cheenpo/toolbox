#!/usr/bin/env python

import sys
import os
import re
import logging
import argparse

"""
author: cyrus (cheenpo@gmail.com)
reason: I wrote this because exporting photos from the macOS application called "Photos"
        does not export them in the basic concept of folders by date    :/
"""


def form_folder(groups):
  """
  take in a date tuple and form the folder name
  """
  month = groups[0]
  day = groups[1]
  year = groups[2]
  if month in month_map:
    month = month_map[month]
  else:
    logger.error("month ({}) not in month_map. this should never happen".format(month))
    return None
  if len(day) == 1:
    day = "0{}".format(day)
  return "{}-{}-{}".format(year, month, day)


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="sanitize iPhoto moment export")
  parser.add_argument("dir", action="store", help="directory to sanitize")
  parser.add_argument('--debug', action='store_true', default=False)
  parser.add_argument('--test', action='store_true', default=False)
  args = parser.parse_args()

  logging_level = logging.INFO
  if args.debug:
    logging_level = logging.DEBUG
  logging.basicConfig(level=logging_level, stream=sys.stdout, format='%(levelname)s %(asctime)s %(message)s', datefmt='%Y-%d-%m %H:%M:%S')
  logger = logging.getLogger(__name__)

  file_rename_limit = 3
  month_map = {
    "January": "01",
    "February": "02",
    "March": "03",
    "April": "04",
    "May": "05",
    "June": "06",
    "July": "07",
    "August": "08",
    "September": "09",
    "October": "10",
    "November": "11",
    "December": "12"
  }
  re_good = r"^\d\d\d\d-\d\d-\d\d$"
  re_match1 = r".*(January|February|March|April|May|June|July|August|September|October|November|December) (\d+), (\d\d\d\d)"
  overall_good = True

  stats = {"files_moved": 0, "files_renamed": 0, "mkdirs": 0, "rmdirs": 0, "stats_fake": args.test}

  logger.info("starting sanity on: {}, test: {}, debug: {}".format(args.dir, args.test, args.debug))
  dirs = [dI for dI in os.listdir(args.dir) if os.path.isdir(os.path.join(args.dir,dI))]
  for dir in dirs:
    orig_path = "{}/{}".format(args.dir, dir)
    if args.dir.endswith("/"):
      orig_path = "{}{}".format(args.dir, dir)

    is_good = re.match(re_good, dir)
    is_match1 = re.match(re_match1, dir)
    dir_good = True if (is_good or is_match1) else False
    overall_good = overall_good and dir_good
    logger.debug("in: {}, is_good: {}, is_match1: {}, dir_good: {}".format(dir, is_good, is_match1, dir_good))
    if is_good:
      logger.info("format is good, skipping: {}".format(dir))
    elif is_match1:
      logger.info("handle match1: {}".format(dir))
      groups = is_match1.groups()
      dst_folder = form_folder(is_match1.groups())
      if dst_folder is None:
        logger.error("skipping dir: {}".format(dir))
        continue
      else:
        # make sure path exists
        dst_path = "{}/{}".format(args.dir, dst_folder)
        if args.dir.endswith("/"):
          dst_path = "{}{}".format(args.dir, dst_folder)

        dst_folder_exists = os.path.isdir(dst_path)
        logger.info("{} exists: {}".format(dst_folder, dst_folder_exists))
        if not dst_folder_exists:
          if args.test:
            logger.info("would mkdir: {}".format(dst_path))
          else:
            logger.info("mkdir: {}".format(dst_path))
            os.mkdir(dst_path)
          stats["mkdirs"] = stats["mkdirs"] + 1

        # move files over
        files = os.listdir(orig_path)
        for file in files:
          i = 0
          orig_file_path = "{}/{}".format(orig_path, file)
          dst_file_path = None
          dst_file_exists = True
          while(dst_file_exists):
            if i > 0:
              logger.info("increasing file rename for {}".format(orig_file_path))
              stats["files_renamed"] = stats["files_renamed"] + 1
            dst_file_path = "{}/{}{}".format(dst_path, "0"*i, file)
            dst_file_exists = os.path.exists(dst_file_path)
            logger.debug("{} -> {}, dst_file_exists: {}".format(orig_file_path, dst_file_path, dst_file_exists))
            i = i + 1
            if i > file_rename_limit:
              logger.error("file_rename_limit exceeded, something is busted")
              sys.exit(1)
          if args.test:
            logger.info("would mv {} -> {}".format(orig_file_path, dst_file_path))
          else:
            logger.info("mv {} -> {}".format(orig_file_path, dst_file_path))
            os.rename(orig_file_path, dst_file_path)
          stats["files_moved"] = stats["files_moved"] + 1

        # delete src dir if empty
        if not os.listdir(orig_path):
          if args.test:
            logger.info("would rmdir {}".format(orig_path))
          else:
            logger.info("rmdir {}".format(orig_path))
            os.rmdir(orig_path)
          stats["rmdirs"] = stats["rmdirs"] + 1

    else:
      logger.warn("unhandled dir: {}".format(dir))

  logger.info(stats)
  logger.info("overall_good: {}".format(overall_good))
