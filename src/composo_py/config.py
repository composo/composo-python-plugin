from dataclasses import dataclass, asdict



# @dataclass
# class App:


# @dataclass
# class Author:
#     name: str
#     email: str
#
#
# @dataclass
# class Git:
#
#
#
# @dataclass
# class VCS:
#     git: Git
#
#
# @dataclass
# class Config:
#     app: App
#     author: Author
#     vcs: VCS
#     dry_run: bool
#
#
# @dataclass
# class Line:
#     a: Point
#     b: Point
#
# line = Line(Point(1,2), Point(3,4))
# assert line == dataclass_from_dict(Line, asdict(line))