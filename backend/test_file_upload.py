import os
import sys
import shutil

def test_upload_directory():
    """测试上传目录创建与权限"""
    print("测试文件上传目录...")
    
    # 测试基本目录
    base_dir = "uploads"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        print(f"创建基本目录: {base_dir}")
    else:
        print(f"基本目录已存在: {base_dir}")
    
    # 测试目录权限
    try:
        test_file = os.path.join(base_dir, "test_write.txt")
        with open(test_file, "w") as f:
            f.write("测试写入权限")
        print(f"目录写入测试成功: {test_file}")
        os.remove(test_file)
        print(f"成功删除测试文件: {test_file}")
    except Exception as e:
        print(f"目录权限测试失败: {str(e)}")
        return False
    
    # 测试会话子目录
    test_session = "session_test"
    session_dir = os.path.join(base_dir, test_session)
    
    if os.path.exists(session_dir):
        try:
            # 尝试删除现有目录，以便重新测试
            shutil.rmtree(session_dir)
            print(f"删除现有会话目录: {session_dir}")
        except Exception as e:
            print(f"无法删除现有会话目录: {str(e)}")
    
    try:
        os.makedirs(session_dir)
        print(f"创建会话目录成功: {session_dir}")
        
        # 测试会话目录写入
        test_file = os.path.join(session_dir, "test_session_file.txt")
        with open(test_file, "w") as f:
            f.write("测试会话目录写入")
        print(f"会话目录写入测试成功: {test_file}")
        
        # 验证文件存在
        if os.path.exists(test_file):
            print(f"文件成功创建: {test_file}")
            # 清理
            os.remove(test_file)
            print(f"清理测试文件: {test_file}")
        else:
            print(f"文件创建失败: {test_file}")
    except Exception as e:
        print(f"会话目录测试失败: {str(e)}")
        return False
    
    print("上传目录测试完成，一切正常!")
    return True

if __name__ == "__main__":
    test_upload_directory() 