export class YiMengQingCheckin extends plugin {
  constructor() {
    super({
      //后端信息
      name: '每日签到',//插件名字，可以随便写
      dsc: '签到',//插件介绍，可以随便写
      event: 'message',//这个直接复制即可，别乱改
      priority: 10,//执行优先级
      rule: [
        {
          //正则表达试
          reg: '^#?怡(签到|怡签到)$',
          //函数
          fnc: 'getcheckin'
        }
      ]
    });
  };
  async getcheckin(e) {
    e.reply("Hello, world!");//输出Hello，world！
    //阻止消息不再往下
    return;
  };

}
