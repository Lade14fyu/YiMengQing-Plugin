// timeUtils.js
import { DateTime, Duration } from 'luxon';

// 设置北京时区
const BEIJING = 'Asia/Shanghai';

function getCurrentTime() {
  return DateTime.now().setZone(BEIJING).toFormat('yyyy-MM-dd HH:mm:ss');
}

function getCurrentDate() {
  return DateTime.now().setZone(BEIJING).toFormat('yyyy-MM-dd');
}

function getTimePeriod() {
  const hour = DateTime.now().setZone(BEIJING).hour;
  if (hour >= 5 && hour < 12) return 'morning';
  if (hour >= 12 && hour < 20) return 'afternoon';
  return 'night';
}

function formatTimestamp(timestamp) {
  return DateTime.fromSeconds(timestamp).setZone(BEIJING).toFormat('yyyy-MM-dd HH:mm:ss');
}

function parseTimeStr(timeStr) {
  try {
    if (timeStr.includes(' ')) {
      return DateTime.fromFormat(timeStr, 'yyyy-MM-dd HH:mm:ss', { zone: BEIJING });
    } else {
      const today = DateTime.now().setZone(BEIJING).toFormat('yyyy-MM-dd');
      return DateTime.fromFormat(`${today} ${timeStr}`, 'yyyy-MM-dd HH:mm', { zone: BEIJING });
    }
  } catch {
    return null;
  }
}

function getTimeDelta(start, end) {
  const diff = end.diff(start, ['days', 'hours', 'minutes', 'seconds']).toObject();
  return {
    days: Math.floor(diff.days || 0),
    hours: Math.floor(diff.hours || 0),
    minutes: Math.floor(diff.minutes || 0),
    seconds: Math.floor(diff.seconds || 0)
  };
}

function isSameDay(time1, time2) {
  const t1 = DateTime.fromJSDate(time1).setZone(BEIJING);
  const t2 = DateTime.fromJSDate(time2).setZone(BEIJING);
  return t1.toFormat('yyyy-MM-dd') === t2.toFormat('yyyy-MM-dd');
}

function getNextTime(targetTime) {
  const now = DateTime.now().setZone(BEIJING);
  const target = parseTimeStr(targetTime);
  if (!target) throw new Error(`无效的时间格式: ${targetTime}`);
  if (now > target) {
    return target.plus({ days: 1 });
  }
  return target;
}

function humanizeTime(dt) {
  const now = DateTime.now().setZone(BEIJING);
  dt = DateTime.fromJSDate(dt).setZone(BEIJING);
  const diff = now.diff(dt, ['days', 'hours', 'minutes', 'seconds']).toObject();

  if (Math.abs(diff.days) > 7) return dt.toFormat('yyyy-MM-dd');
  if (Math.abs(diff.days) > 1) return `${Math.floor(Math.abs(diff.days))}天前`;
  if (Math.abs(diff.days) === 1) return '昨天';
  if (Math.abs(diff.hours) >= 1) return `${Math.floor(Math.abs(diff.hours))}小时前`;
  if (Math.abs(diff.minutes) >= 1) return `${Math.floor(Math.abs(diff.minutes))}分钟前`;
  return '刚刚';
}

export {
  getCurrentTime,
  getCurrentDate,
  getTimePeriod,
  formatTimestamp,
  parseTimeStr,
  getTimeDelta,
  isSameDay,
  getNextTime,
  humanizeTime
};
