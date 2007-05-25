--
-- Combine the Chapter and ReleasedChapter into a single model
-- This will let chapters be moved in future versions.
-- Kinda gross SQL, but whatever.
--

BEGIN;

ALTER TABLE djangobook_chapter RENAME TO old_chapter;
ALTER TABLE djangobook_comment RENAME TO old_comment;

CREATE TABLE "djangobook_chapter" (
    "id" serial NOT NULL PRIMARY KEY,
    "type" varchar(1) NOT NULL,
    "number" smallint CHECK ("number" >= 0) NOT NULL,
    "title" varchar(200) NOT NULL,
    "version_id" integer NOT NULL,
    "release_date" timestamp with time zone NULL,
    "comments_open" boolean NOT NULL,
    "_old_id" INTEGER,
    UNIQUE ("type", "number", "version_id")
);
CREATE TABLE "djangobook_comment" (
    "id" serial NOT NULL PRIMARY KEY,
    "chapter_id" integer NOT NULL REFERENCES "djangobook_chapter" ("id") DEFERRABLE INITIALLY DEFERRED,
    "name" varchar(50) NOT NULL,
    "email" varchar(75) NOT NULL,
    "url" varchar(200) NOT NULL,
    "nodenum" smallint CHECK ("nodenum" >= 0) NOT NULL,
    "comment" text NOT NULL,
    "date_posted" timestamp with time zone NOT NULL,
    "is_removed" boolean NOT NULL,
    "is_reviewed" boolean NOT NULL
);

INSERT INTO djangobook_chapter
  (type, "number", title, version_id, release_date, comments_open, _old_id)
SELECT 
  c.type, 
  c.number, 
  c.title, 
  COALESCE(r.version_id, 1), 
  r.release_date, 
  COALESCE(r.comments_open, true), 
  r.id
FROM old_chapter AS c 
LEFT JOIN djangobook_releasedchapter AS r ON c.id = r.chapter_id;

INSERT INTO djangobook_comment
  (chapter_id, name, email, url, nodenum, comment, date_posted, is_removed, is_reviewed)
SELECT
  (SELECT id FROM djangobook_chapter WHERE _old_id = old_comment.chapter_id),
  name, 
  email,
  url,
  nodenum,
  comment, 
  date_posted,
  is_removed,
  is_reviewed
FROM old_comment;

ALTER TABLE djangobook_chapter DROP COLUMN _old_id;
DROP TABLE old_comment;
DROP TABLE djangobook_releasedchapter;
DROP TABLE old_chapter;

COMMIT;