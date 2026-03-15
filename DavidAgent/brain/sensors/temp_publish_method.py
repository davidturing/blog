    def publish_to_github_tech_repo(self, report: str, insights: List[Dict[str, Any]]):
        """发布报告到 GitHub tech 仓库"""
        try:
            success = self.github_publisher.publish_report(report, insights)
            if success:
                self.logger.info("✅ 报告已成功发布到 GitHub tech 仓库")
            else:
                self.logger.warning("⚠️ 报告发布到 GitHub 失败，但本地保存成功")
        except Exception as e:
            self.logger.error(f"❌ GitHub 发布异常: {e}")