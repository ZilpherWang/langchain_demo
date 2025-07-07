from mcp.server.fastmcp import FastMCP

mcp = FastMCP("guidanceServer")


@mcp.tool()
def patient_info(user_id: str):
    """获取某个用户的就诊记录
        Args:
            user_id: 用户编号
        Returns:
            就诊记录
    """
    return [
        {"user_id": user_id, "diagnosis_info": "前列腺炎", "date": "2024-03-02"},
        {"user_id": user_id, "diagnosis_info": "前列腺囊肿", "date": "2025-05-05"},
        {"user_id": user_id, "diagnosis_info": "过敏性皮炎", "date": "2024-12-20"},
        {"user_id": user_id, "diagnosis_info": "鼻炎水肿", "date": "2024-10-12"},
        {"user_id": user_id, "diagnosis_info": "右膝内侧副韧带损伤", "date": "2025-03-07"},
    ]

if __name__ == "__main__":
    mcp.run(transport="sse")