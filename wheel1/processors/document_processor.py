"""
文档处理器 - 支持多模态输入
包括文本、PDF、图像、视频处理
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from abc import ABC, abstractmethod

from core.modes import ProcessingMode

logger = logging.getLogger(__name__)


class TextExtractor(ABC):
    """文本提取器基类"""
    
    @abstractmethod
    def extract(self, file_path: str) -> str:
        """从文件提取文本"""
        pass


class PDFExtractor(TextExtractor):
    """PDF文本提取"""
    
    def extract(self, file_path: str) -> str:
        """从PDF提取文本"""
        try:
            import PyPDF2
            
            text = []
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text.append(page.extract_text())
            
            return '\n'.join(text)
        
        except ImportError:
            logger.warning("PyPDF2未安装，使用简单文本提取")
            return f"[PDF内容] 文件: {file_path}"


class DocXExtractor(TextExtractor):
    """Word文档文本提取"""
    
    def extract(self, file_path: str) -> str:
        """从DOCX提取文本"""
        try:
            from docx import Document
            
            doc = Document(file_path)
            text = []
            for para in doc.paragraphs:
                text.append(para.text)
            
            return '\n'.join(text)
        
        except ImportError:
            logger.warning("python-docx未安装，使用简单文本提取")
            return f"[Word内容] 文件: {file_path}"


class ImageExtractor(TextExtractor):
    """图像文本提取（OCR）"""
    
    def __init__(self, mode: ProcessingMode = ProcessingMode.BALANCED):
        """
        初始化图像提取器
        
        Args:
            mode: 处理模式（影响OCR模型选择）
        """
        self.mode = mode
        self._initialize_ocr()
    
    def _initialize_ocr(self):
        """根据模式初始化OCR"""
        if self.mode == ProcessingMode.EFFICIENCY:
            # 高效模式：使用轻量级OCR
            self.ocr_type = 'easyocr'
        elif self.mode == ProcessingMode.BALANCED:
            # 中效模式：使用Paddle OCR
            self.ocr_type = 'paddle'
        else:  # PRECISION
            # 低效模式：使用最强OCR（GPT-4V）
            self.ocr_type = 'gpt4v'
        
        logger.info(f"初始化OCR: {self.ocr_type} (模式: {self.mode.value})")
    
    def extract(self, file_path: str) -> str:
        """从图像提取文本"""
        try:
            if self.ocr_type == 'easyocr':
                return self._extract_easyocr(file_path)
            elif self.ocr_type == 'paddle':
                return self._extract_paddle_ocr(file_path)
            else:
                return self._extract_gpt4v(file_path)
        
        except Exception as e:
            logger.error(f"OCR提取失败: {e}")
            return f"[图像内容] 文件: {file_path} (OCR失败)"
    
    def _extract_easyocr(self, file_path: str) -> str:
        """使用EasyOCR提取（快速）"""
        try:
            import easyocr
            reader = easyocr.Reader(['ch', 'en'])
            result = reader.readtext(file_path)
            return '\n'.join([text[1] for text in result])
        except ImportError:
            logger.warning("easyocr未安装")
            return ""
    
    def _extract_paddle_ocr(self, file_path: str) -> str:
        """使用PaddleOCR提取（平衡）"""
        try:
            from paddleocr import PaddleOCR
            ocr = PaddleOCR(use_angle_cls=True, lang='ch')
            result = ocr.ocr(file_path, cls=True)
            return '\n'.join([line[0][1] for line in result if result])
        except ImportError:
            logger.warning("paddleocr未安装")
            return ""
    
    def _extract_gpt4v(self, file_path: str) -> str:
        """使用GPT-4V提取（最精确）"""
        try:
            import base64
            from openai import OpenAI
            
            client = OpenAI()
            
            # 读取图像并编码
            with open(file_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # 调用GPT-4V
            response = client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            },
                            {
                                "type": "text",
                                "text": "请完整地识别和提取图像中的所有文本内容"
                            }
                        ]
                    }
                ]
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.warning(f"GPT-4V提取失败: {e}")
            return ""


class VideoExtractor(TextExtractor):
    """视频文本提取"""
    
    def extract(self, file_path: str) -> str:
        """从视频提取文本（字幕、语音识别）"""
        try:
            # 这里应实现视频处理逻辑
            # 包括：提取字幕、语音转文字、场景识别等
            logger.info(f"处理视频文件: {file_path}")
            return f"[视频内容] 文件: {file_path}\n[需要实现视频处理模块]"
        
        except Exception as e:
            logger.error(f"视频提取失败: {e}")
            return ""


class DocumentProcessor:
    """统一文档处理器"""
    
    # 文件类型到提取器的映射
    EXTRACTORS = {
        '.pdf': PDFExtractor,
        '.docx': DocXExtractor,
        '.doc': DocXExtractor,
        '.txt': lambda: None,  # 直接读取
        '.jpg': ImageExtractor,
        '.jpeg': ImageExtractor,
        '.png': ImageExtractor,
        '.mp4': VideoExtractor,
        '.avi': VideoExtractor
    }
    
    def __init__(
        self,
        mode: ProcessingMode = ProcessingMode.BALANCED,
        cache: Optional[Any] = None
    ):
        """
        初始化文档处理器
        
        Args:
            mode: 处理模式
            cache: 缓存管理器（可选）
        """
        self.mode = mode
        self.cache = cache
        self.extractors = {}
        
        logger.info(f"初始化文档处理器 - 模式: {mode.value}")
    
    def extract_text(
        self,
        file_path: str,
        mode: Optional[ProcessingMode] = None
    ) -> str:
        """
        从文档提取文本
        
        Args:
            file_path: 文件路径
            mode: 处理模式（可覆盖默认模式）
        
        Returns:
            提取的文本
        """
        mode = mode or self.mode
        
        # 检查缓存
        cache_key = f"extract:{file_path}:{mode.value}"
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                logger.info(f"使用缓存文本提取: {file_path}")
                return cached
        
        # 确定文件类型和提取器
        file_path_obj = Path(file_path)
        ext = file_path_obj.suffix.lower()
        
        # 特殊处理：纯文本文件
        if ext == '.txt':
            text = self._read_text_file(file_path)
        else:
            # 获取或创建提取器
            extractor = self._get_extractor(ext, mode)
            
            if extractor is None:
                logger.warning(f"不支持的文件类型: {ext}")
                text = ""
            else:
                text = extractor.extract(file_path)
        
        # 存储到缓存
        if self.cache and text:
            self.cache.set(cache_key, text, ttl=86400)  # 24小时TTL
        
        logger.info(f"文本提取完成: {file_path} ({len(text)} 字符)")
        return text
    
    def _get_extractor(
        self,
        file_ext: str,
        mode: ProcessingMode
    ) -> Optional[TextExtractor]:
        """获取或创建提取器实例"""
        
        cache_key = f"{file_ext}:{mode.value}"
        
        if cache_key not in self.extractors:
            extractor_class = self.EXTRACTORS.get(file_ext)
            
            if extractor_class is None:
                return None
            
            # 某些提取器需要mode参数
            if file_ext in {'.jpg', '.jpeg', '.png'}:
                self.extractors[cache_key] = extractor_class(mode)
            else:
                self.extractors[cache_key] = extractor_class()
        
        return self.extractors.get(cache_key)
    
    def _read_text_file(self, file_path: str) -> str:
        """读取纯文本文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # 尝试其他编码
            with open(file_path, 'r', encoding='gbk') as f:
                return f.read()
    
    def batch_extract(
        self,
        file_paths: List[str]
    ) -> Dict[str, str]:
        """批量提取文本"""
        results = {}
        for file_path in file_paths:
            try:
                results[file_path] = self.extract_text(file_path)
            except Exception as e:
                logger.error(f"批量提取失败: {file_path} - {e}")
                results[file_path] = None
        
        return results
