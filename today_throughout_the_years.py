#!/usr/bin/env python3

import sys
import os
import re
import logging
import argparse
import shutil
from datetime import datetime
from pathlib import Path

"""
author: cyrus (cheenpo@gmail.com)
reason: I wrote this because I would like to see all the photos of today from every year
"""



if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="collect photos for the day throughout the year")
  parser.add_argument("dir", action="store", help="directory to work in")
  parser.add_argument('--debug', action='store_true', default=False)
  parser.add_argument('--test', action='store_true', default=False)
  args = parser.parse_args()

  logging_level = logging.INFO
  if args.debug:
    logging_level = logging.DEBUG
  logging.basicConfig(level=logging_level, stream=sys.stdout, format='%(levelname)s %(asctime)s %(message)s', datefmt='%Y-%d-%m %H:%M:%S')
  logger = logging.getLogger(__name__)

  logger.info("creating today from: {}, test: {}, debug: {}".format(args.dir, args.test, args.debug))
  #
  home_folder = Path.home()
  today_folder = "{}/Downloads/today".format(home_folder)
  today_folder_exists = os.path.isdir(today_folder)
  logger.info("{} exists: {}".format(today_folder, today_folder_exists))
  if today_folder_exists:
    if args.test:
      logger.info("would remove files: {} : but testing".format(today_folder))
    else:
      logger.info("removing existing files: {}".format(today_folder))
      files = os.listdir(today_folder)
      for f in files:
        ff = "{}/{}".format(today_folder, f)
        logger.warning("removing: {}".format(ff))
        os.remove(ff)
  else:
    logger.info("creating folder: {}".format(today_folder))
    os.mkdir(today_folder)
  #

  #
  stats = {"files_copied": 0, "stats_fake": args.test}
  re_good_folder = r"^\d\d\d\d-\d\d-\d\d$"
  day_of_year = datetime.today().strftime("%m-%d")
  re_correct_folder = r"^\d\d\d\d-{}$".format(day_of_year)
  #
  dirs = [dI for dI in os.listdir(args.dir) if os.path.isdir(os.path.join(args.dir,dI))]
  for dir in dirs:
    orig_path = "{}/{}".format(args.dir, dir)
    if args.dir.endswith("/"):
      orig_path = "{}{}".format(args.dir, dir)

    is_good = re.match(re_good_folder, dir)
    if is_good:
      logger.debug("dir is good: {}".format(dir))
      is_correct = re.match(re_correct_folder, dir)
      if is_correct:
        logger.debug("dir is correct: {}".format(dir))
        files = os.listdir("{}/{}".format(args.dir, dir))
        for f in files:
          ff_src = "{}/{}/{}".format(args.dir, dir, f)
          ff_dst = "{}/{}---{}".format(today_folder, dir, f)
          stats["files_copied"] = stats["files_copied"] + 1
          if args.test:
            logger.info("would copy: {} -> {} : but testing".format(ff_src, ff_dst))
          else:
            logger.info("copying: {} -> {}".format(ff_src, ff_dst))
            shutil.copyfile(ff_src, ff_dst)

        #
    else:
      logger.debug("dir is bad: {} : skipping".format(dir))

  logger.info(stats)
