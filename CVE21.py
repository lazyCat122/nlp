import os
import subprocess
import re

# 配置部分
repository_url = "https://github.com/example/repository.git"  # 目标仓库的 URL
local_repo_path = "./git_project"  # 下载到本地的路径
vulnerability_keyword = "first commit"  # 用于搜索的漏洞关键词 "CVE-20"

# Step 1: 克隆 Git 仓库
def clone_repository(repo_url, path):
    if os.path.exists(path):
        print(f"Repository already exists at {path}. Skipping clone.")
    else:
        print(f"Cloning repository from {repo_url} to {path}...")
        try:
            result = subprocess.run(
                ["git", "clone", repo_url, path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            print(result.stdout)  # 输出克隆的详细信息
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while cloning repository: {e.stderr}")

# Step 2: 获取包含漏洞关键词的提交记录
def search_vulnerable_commits(path, keyword):
    print(f"Searching for commits with keyword '{keyword}'...")
    os.chdir(path)
    result = subprocess.run(["git", "log", "--grep", keyword, "--pretty=format:%H %s"],#%H %s：哈希值，提交说明
                            stdout=subprocess.PIPE, text=True)
    commits = result.stdout.splitlines()
    return commits

# Step 3: 显示并过滤提交记录
def filter_commits(commits):
    filtered_commits = []
    for commit in commits:
        if not re.search(r"\b(revert|merge|update)\b", commit, re.IGNORECASE):
            filtered_commits.append(commit.split()[0])  # 提取提交的哈希值（40个字符）
    return filtered_commits

#tdout 是 subprocess.run 返回的结果对象的一个属性，表示标准输出（Standard Output）
# 在命令行或终端中，标准输出通常是显示命令运行结果的地方。
#在 subprocess.run 中，如果我们设置了 stdout=subprocess.PIPE，则运行命令后的输出会被捕获，并存储在返回对象的 stdout 属性中。

# Step 4: 提取未修补的文件版本
def extract_vulnerable_code(commit_hash):
    print(f"Extracting vulnerable code from commit {commit_hash}...")
    diff_output = subprocess.run(["git", "show", commit_hash], stdout=subprocess.PIPE, text=True)
    # 解析 diff 输出以获取旧文件的内容
    return diff_output.stdout

# 主函数
def main():
    # 克隆仓库
    clone_repository(repository_url, local_repo_path)

    # 查找包含漏洞关键词的提交
    commits = search_vulnerable_commits(local_repo_path, vulnerability_keyword)
    print(f"Found {len(commits)} commits with the keyword '{vulnerability_keyword}'.")

    # 过滤不相关的提交,并提取对应的哈希值
    filtered_commits = filter_commits(commits)
    print(f"{len(filtered_commits)} relevant commits after filtering.")
    print(filtered_commits)

    # 提取并显示未修补的代码
    for commit_hash in filtered_commits:
        vulnerable_code = extract_vulnerable_code(commit_hash)
        print(f"Vulnerable code in commit {commit_hash}:\n{vulnerable_code}")

if __name__ == "__main__":
    main()
