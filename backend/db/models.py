from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Float,
    UniqueConstraint,
)
from sqlalchemy.sql import func

from db.database import Base


class ConfigFile(Base):
    __tablename__ = "config_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_hash = Column(String, nullable=False, unique=True, index=True)
    raw_config = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Framework(Base):
    __tablename__ = "frameworks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    version = Column(String, nullable=True)
    source = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


class FrameworkRule(Base):
    __tablename__ = "framework_rules"

    id = Column(Integer, primary_key=True, index=True)
    framework_id = Column(
        Integer,
        ForeignKey("frameworks.id"),
        nullable=False,
    )
    control_id = Column(String, nullable=False)
    category = Column(String, nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    sbm_field_path = Column(String, nullable=False)
    expected_value = Column(String, nullable=True)
    operator = Column(
        String,
        nullable=False,
        default="eq",
    )
    severity = Column(
        String,
        nullable=False,
        default="HIGH",
    )
    remediation_hint = Column(Text, nullable=True)


class SecurityBaselineModel(Base):
    __tablename__ = "security_baseline_models"

    id = Column(Integer, primary_key=True, index=True)

    config_file_id = Column(
        Integer,
        ForeignKey("config_files.id"),
        nullable=False,
        unique=True,
    )

    vendor = Column(String, nullable=False)
    os = Column(String, nullable=False)
    hostname = Column(String, nullable=True)

    sbm_json = Column(Text, nullable=False)

    confidence = Column(
        Float,
        nullable=False,
    )

    unknown_blocks_json = Column(
        Text,
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

class Audit(Base):
    __tablename__ = "audits"

    id = Column(Integer, primary_key=True, index=True)

    config_file_id = Column(
        Integer,
        ForeignKey("config_files.id"),
        nullable=False,
    )

    framework_id = Column(
        Integer,
        ForeignKey("frameworks.id"),
        nullable=False,
    )

    total_controls = Column(
        Integer,
        nullable=False,
    )

    passed = Column(
        Integer,
        nullable=False,
    )

    failed = Column(
        Integer,
        nullable=False,
    )

    score = Column(
        Float,
        nullable=False,
    )

    findings_json = Column(
        Text,
        nullable=False,
    )

    pdf_path = Column(
        String,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

class RemediationCache(Base):
    __tablename__ = "remediation_cache"

    id = Column(Integer, primary_key=True, index=True)

    vendor = Column(
        String,
        nullable=False,
    )

    control_id = Column(
        String,
        nullable=False,
    )

    remediation_json = Column(
        Text,
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    __table_args__ = (
        UniqueConstraint(
            "vendor",
            "control_id",
            name="uq_remediation_vendor_control",
        ),
    )