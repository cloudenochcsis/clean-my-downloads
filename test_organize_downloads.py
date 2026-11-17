import unittest
import tempfile
import time
import sys
from pathlib import Path
import hashlib

sys.path.insert(0, str(Path(__file__).parent.resolve()))

# Import from organize_downloads (will fail initially if new functions are missing)
from organize_downloads import (
    classify_item,
    is_recent,
    is_in_progress,
    is_hidden_or_system,
    resolve_destination,
)


class TestOrganizeDownloads(unittest.TestCase):
    def test_phd_classification(self):
        self.assertEqual(classify_item(Path("Full_Proposal_v4.10.1_Panel_Corrections_Tracked.docx")), "PhD Research")
        self.assertEqual(classify_item(Path("Addressing Panel Feedback v4.10.1.docx")), "PhD Research")
        self.assertEqual(classify_item(Path("Feedback_PhD_Defence.docx")), "PhD Research")
        self.assertEqual(classify_item(Path("Panel_Feedback_Response_and_Correction_Matrix.docx")), "PhD Research")

    def test_job_hunting_classification(self):
        self.assertEqual(classify_item(Path("Enoch Kalmus-Resume.pdf")), "Job Hunting Resumes")
        self.assertEqual(classify_item(Path("Enoch_Ayivor_LinkedIn Resume.pdf")), "Job Hunting Resumes")
        self.assertEqual(classify_item(Path("Enoch_Ayivor_UNICC_Motivation_Letter.docx")), "Job Hunting Resumes")
        self.assertEqual(classify_item(Path("Cloud Platform Support Engineer (Azure Operations) — AmaliTech (Application).pdf")), "Job Hunting Resumes")

    def test_books_and_guides_classification(self):
        self.assertEqual(classify_item(Path("CompTIA Security+ Review Guide.azw")), "Documents/Books & Guides")
        self.assertEqual(classify_item(Path("James Pengelly - CompTIA CySA+ Student Guide - libgen.li.pdf")), "Documents/Books & Guides")
        self.assertEqual(classify_item(Path("SACLA_2026_Proceedings_Final.pdf")), "Documents/Books & Guides")
        self.assertEqual(classify_item(Path("SecurityPlus Exam Guide.epub")), "Documents/Books & Guides")

    def test_personal_admin_classification(self):
        self.assertEqual(classify_item(Path("Ticket - Enoch Ayivor.pdf")), "Documents/Personal & Admin")
        self.assertEqual(classify_item(Path("Payment Notification.pdf")), "Documents/Personal & Admin")
        self.assertEqual(classify_item(Path("Proof of Registration.pdf")), "Documents/Personal & Admin")
        self.assertEqual(classify_item(Path("Source of Income Declaration.pdf")), "Documents/Personal & Admin")
        self.assertEqual(classify_item(Path("gitlab-recovery-codes.txt")), "Documents/Personal & Admin")

    def test_database_backup_classification(self):
        self.assertEqual(classify_item(Path("coopisland__prod_DB_backup.sql")), "Documents/Database Backups")
        self.assertEqual(classify_item(Path("mydb_dump.sql")), "Documents/Database Backups")

    def test_course_directory_classification(self):
        self.assertEqual(classify_item(Path("[ WebToolTip.com ] Udemy - AI Agents in Production"), is_dir=True), "Courses")
        self.assertEqual(classify_item(Path("Code with Mosh - Claude Code for Professional Developers"), is_dir=True), "Courses")
        self.assertEqual(classify_item(Path("Learn DevOps The Complete Kubernetes Course"), is_dir=True), "Courses")
        self.assertEqual(classify_item(Path("GitHub Actions - The Complete Guide"), is_dir=True), "Courses")

    def test_movie_directory_classification(self):
        self.assertEqual(classify_item(Path("Greyhound (2020) (1080p ATVP WEB-DL x265)"), is_dir=True), "Videos")
        self.assertEqual(classify_item(Path("The Odyssey (2026) (1080p AMZN WEB-DL)"), is_dir=True), "Videos")

    def test_temporary_lock_files(self):
        self.assertEqual(classify_item(Path("~$hedule_of_Corrections_PhD_Defence.docx")), "redundant files")

    def test_fallback_extensions(self):
        self.assertEqual(classify_item(Path("Cursor-darwin-arm64.dmg")), "Applications")
        self.assertEqual(classify_item(Path("bundle.tar.gz")), "Archives")
        self.assertEqual(classify_item(Path("photo.jpg")), "Images")
        self.assertEqual(classify_item(Path("photo.heic")), "Images")
        self.assertEqual(classify_item(Path("video.mp4")), "Videos")
        self.assertEqual(classify_item(Path("sample.docx")), "Documents")
        self.assertEqual(classify_item(Path("random.xyz123")), "Others")

    def test_in_progress_and_hidden(self):
        self.assertTrue(is_in_progress(Path("file.pdf.crdownload")))
        self.assertTrue(is_in_progress(Path("file.iso.part")))
        self.assertFalse(is_in_progress(Path("file.pdf")))

        self.assertTrue(is_hidden_or_system(Path(".DS_Store")))
        self.assertTrue(is_hidden_or_system(Path(".localized")))
        self.assertTrue(is_hidden_or_system(Path(".git")))
        self.assertFalse(is_hidden_or_system(Path("normal_file.pdf")))

    def test_is_recent(self):
        with tempfile.NamedTemporaryFile() as tmp:
            tmp_path = Path(tmp.name)
            self.assertTrue(is_recent(tmp_path, min_age_seconds=120))

    def test_duplicate_routing_same_hash(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            downloads = tmp_path / "Downloads"
            dest_dir = downloads / "Documents"
            redundant_dir = downloads / "redundant files"
            dest_dir.mkdir(parents=True)
            redundant_dir.mkdir(parents=True)

            content = b"Exact same content in both files"
            existing = dest_dir / "report.pdf"
            existing.write_bytes(content)

            incoming = downloads / "report.pdf"
            incoming.write_bytes(content)

            routed = resolve_destination(downloads, dest_dir, incoming)
            self.assertEqual(routed.parent, redundant_dir)
            self.assertEqual(routed.name, "report (duplicate).pdf")

    def test_duplicate_routing_different_hash(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            downloads = tmp_path / "Downloads"
            dest_dir = downloads / "Documents"
            dest_dir.mkdir(parents=True)

            existing = dest_dir / "report.pdf"
            existing.write_bytes(b"Original content version 1")

            incoming = downloads / "report.pdf"
            incoming.write_bytes(b"Different content version 2")

            routed = resolve_destination(downloads, dest_dir, incoming)
            self.assertEqual(routed.parent, dest_dir)
            self.assertEqual(routed.name, "report (1).pdf")


if __name__ == "__main__":
    unittest.main()
