class TodoCli < Formula
  include Language::Python::Virtualenv

  desc "Simple, beautiful command-line todo application for developers"
  homepage "https://github.com/yourusername/todo-cli"
  url "https://github.com/yourusername/todo-cli/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "REPLACE_WITH_ACTUAL_SHA256_AFTER_RELEASE"
  license "MIT"

  depends_on "python@3.9"

  resource "click" do
    url "https://files.pythonhosted.org/packages/59/87/84326af34517fca8c58418d148f2403df25303e02736832403587318e9e8/click-8.1.3.tar.gz"
    sha256 "7682dc8afb30297001674575ea00d1814d808d6a36af415a82bd481d37ba7b8e"
  end

  resource "rich" do
    url "https://files.pythonhosted.org/packages/11/23/814edf09ec6470d52022b9e95c23c1bef77f0bc451761e1504ebd09606d3/rich-12.6.0.tar.gz"
    sha256 "ba3a3775974105c221d31141f2c116f4fd65c5ceb0698657a11e9f295ec93fd0"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    # Add a todo and verify it was added
    assert_match "Added todo", shell_output("#{bin}/todo a 'Test todo'")
    assert_match "Test todo", shell_output("#{bin}/todo l")
  end
end
